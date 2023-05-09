import math

from typing import Literal


Fo = float | None


def f(x: Fo) -> float:
    if x is None:
        raise ValueError("Cannot use None in this context")
    return x


def ln(x: float) -> float:
    return math.log(x, math.e)


class Gas:
    st = 300.0
    sp = 100_000.0
    # J / K
    R = 8.314

    lock_mode_text = {
        "P": "Isobaric",
        "T": "Isothermal",
        "V": "Isometric",
        None: "Adiabatic",
    }

    symbol_meaning = {
        "T": "Temperature",
        "P": "Pressure",
        "V": "Volume",
    }

    @staticmethod
    def stp_air():
        return Gas(T=Gas.st, P=Gas.sp)

    def __init__(
        self,
        gamma: float = 1.4,
        atomic_mass: float = 28.97,
        T: Fo = None,
        P: Fo = None,
        V: Fo = None,
    ):
        """
        Initializes a three variable system

        Mass is not a variable, as we assume 1 mol of gas
        """
        if (v := len([d for d in [T, P, V] if d])) != 2:
            raise ValueError(
                f"Must specify exactly two of T, P, V. {v} variables given"
            )
        self.gamma = gamma
        self.atomic_mass = atomic_mass

        self.C_v = self.R / (self.gamma - 1)  # Good approximation for air

        # PV=NkT | nRT
        # We assume n = 1 mol
        self._T = T if T is not None else f(P) * f(V) / self.R
        self._P = P if P is not None else f(V) * self.R / self._T
        self._V = self.R * self._T / self._P

        self.locked: None | Literal["P"] | Literal["T"] | Literal["V"] = None

        self._S = 0
        self._current_S = 0

        self._W = 0
        self._current_work = 0

    @property
    def T(self):
        return self._T

    @property
    def P(self):
        return self._P

    @property
    def V(self):
        return self._V

    def lock(self, var: Literal["P", "T", "V"]):
        if var not in ["P", "T", "V"]:
            raise ValueError("Invalid variable. Must be P, T or V")
        self.locked = var

    def unlock(self):
        self.locked = None

    def _update_variables(self, P: float, V: float, T: float):
        """
        Also used to update entropy and work
        """
        self._current_S += self.C_v * ln(T / self._T) + self.R * ln(V / self._V)

        # Calculate work done
        if self._V == V:
            pass
        elif self._P == P:
            self._current_work += P * (V - self._V)
        else:
            if self.locked is None:
                self._current_work += (
                    P
                    * V**self.gamma
                    * (V ** (1 - self.gamma) - self._V ** (1 - self.gamma))
                    / (1 - self.gamma)
                )
            elif self.locked == "T":
                self._current_work += T * ln(V / self._V)
            else:
                raise Exception("The code is wrong")

        self._P = P
        self._V = V
        self._T = T

    def check_lockmode(self, var: Literal["P", "T", "V"]):
        if self.locked == var:
            raise ValueError(
                f"Cannot change {self.symbol_meaning[var]} in {self.lock_mode_text[self.locked]} process"
            )

    def _invalid_lock_exception(self):
        if self.locked is None or self.locked not in ["P", "T", "V"]:
            return Exception("The code is wrong")

        return Exception(
            f"The lock mode is invalid. Expected one of P, T, V or None, got {self.locked}"
        )

    @T.setter
    def T(self, T: float):
        self.check_lockmode("T")

        _P = self._P
        _V = self._V
        # _T = self._T

        # PV ~ T
        if self.locked == "P":
            _V *= T / self._T
        elif self.locked == "V":
            _P *= T / self._T
        elif self.locked is None:
            # Adiabatic
            _P *= (self._T / T) ** (self.gamma / (1 - self.gamma))
            _V *= (self._T / T) ** (1 / (self.gamma - 1))
        else:
            raise self._invalid_lock_exception()

        self._update_variables(_P, _V, T)

    @P.setter
    def P(self, P: float):
        self.check_lockmode("P")

        # _P = self._P
        _V = self._V
        _T = self._T

        if self.locked == "V":
            _T *= P / self._P
        elif self.locked == "T":
            # Heat is provided
            _V *= self._P / P
        elif self.locked is None:
            # Adiabatic
            _T *= (self._P / P) ** ((1 - self.gamma) / self.gamma)
            _V *= (self._P / P) ** (1 / self.gamma)
        else:
            raise self._invalid_lock_exception()

        self._update_variables(P, _V, _T)

    @V.setter
    def V(self, V: float):
        self.check_lockmode("V")

        _P = self._P
        _T = self._T
        # _V = self._V

        if self.locked == "P":
            _T *= V / self._V
        elif self.locked == "T":
            # Heat is proided
            _P *= self._V / V
        elif self.locked is None:
            # Adiabatic
            _T *= (self._V / V) ** (self.gamma - 1)
            _P *= (self._V / V) ** self.gamma
        else:
            raise self._invalid_lock_exception()

        self._update_variables(_P, V, _T)

    @property
    def U(self):
        return self.R * self._T / (self.gamma - 1)

    @property
    def H(self):
        return self.U + self._P * self._V

    @property
    def S(self):
        """
        Sets dS to 0 and returns current entropy
        """
        self.dS
        return self._S

    @property
    def W(self):
        """
        Sets dW to 0 and returns current work
        """
        self.dW
        return self._W

    @property
    def dS(self):
        """
        Returns entropy change. Obtaining this value will set this value to 0 and update absolute entropy
        """
        dS = self._current_S - self._S
        self._S = self._current_S
        return dS

    @property
    def dW(self):
        """
        Returns work done. Obtaining this value will set this value to 0 and update total work
        """
        dW = self._current_work
        self._W += self._current_work
        self._current_work = 0
        return dW

    def __repr__(self):
        return f"Gas(T={self.T:.1f}K, P={self.P / 1000:.1f}kPa, V={self.V * 1000:.1f}L, S={self._current_S:.1f} + C J/K, mode={self.lock_mode_text[self.locked]})"

    @property
    def density(self):
        return self.atomic_mass / self.V


__all__ = ["Gas"]
