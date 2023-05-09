"""
File containing Ideal open Brayton cycle jet engines excluding ramjets and scramjets
"""


from types import SimpleNamespace


def kt_to_ms(kt: float) -> float:
    """
    Convert knots to meters per second
    """
    return kt * 0.514444444


def temp_to_p_r(temperature: float) -> float:
    """
    Approximation for P_r (good for temp < 1300K ish)
    """
    return (temperature / 283) ** 3.8 + 0.029


def p_r_to_temp(p_r: float) -> float:
    """
    Approximation for temperature (good for temp < 1300K ish)
    """
    return (p_r - 0.029) ** (1 / 3.8) * 283


def temp_to_h(temperature: float) -> float:
    """
    Approximation for h
    """
    return temperature + (temperature / 130) ** 2


def h_to_temp(h: float) -> float:
    """
    Approximation for temperature
    """
    return h - (h / 130) ** 2


class JetEngine:
    @staticmethod
    def efficiency(
        mass_flowrate: float,
        velocity_out: float,
        velocity_in: float,
        velocity_engine: float,
        heat_flowrate: float,
    ):
        """
        `velocity_engine` is the velocity of the engine relative to the air
        """
        return (
            mass_flowrate
            * (velocity_out - velocity_in)
            * velocity_engine
            / heat_flowrate
        )

    def __init__(self):
        pass


"""
6 stages


1 before entering
2 entering diffuser. slight pressure and temperature increase. isentropic
3 compressor. pressure and temperature increase. isentropic
4 combustion chamber. pressure and temperature increase. isobaric (increase in entropy here)
5 turbine. pressure and temperature decrease. isentropic
6 after leaving. pressure and temperature decrease. isentropic
"""

# Given by 0.287 kPa * m^3 / kg * K
R = 287


class Info(SimpleNamespace):
    pass


class Turbojet:
    """
    Turbojet engine
    """

    def __init__(
        self,
        inlet_area: float,
        exit_area: float,
        inlet_pressure: float,
        exit_pressure: float,
        compresser_ratio: float,
        inlet_temperature: float,
        diffuser_pressure_increase: float,
    ):
        self.inlet_area = inlet_area
        self.exit_area = exit_area
        self.inlet_pressure = inlet_pressure
        self.exit_pressure = exit_pressure
        self.compresser_ratio = compresser_ratio
        self.inlet_temperature = inlet_temperature
        self.diffuser_pressure_increase = diffuser_pressure_increase

    def calculate(self, temperature: float, velocity: float) -> Info:
        """
        Directly taken from p. 424
        """
        P1 = self.inlet_pressure
        T1 = temperature

        P2 = P1 + self.diffuser_pressure_increase
        P3 = P2 * self.compresser_ratio

        P4 = P3

        T4 = self.inlet_temperature
        P6 = self.exit_pressure

        # states 1 and 3 are connected by an isentropic path
        P13r = P3 / P1

        # Temperature at state 3 may be determined using reduced pressure value
        Pr1 = temp_to_p_r(T1)
        Pr3 = P13r * Pr1
        T3 = p_r_to_temp(Pr3)
        H3 = temp_to_h(T3)

        # print("T3 (should be 511)", T3)

        # states 4 and 6 are connected by an isentropic path
        P64r = P6 / P4
        Pr4 = temp_to_p_r(T4)
        H4 = temp_to_h(T4)
        Pr6 = P64r * Pr4
        T6 = p_r_to_temp(Pr6)

        # print("T6 (should be 557)", T6)

        # mass flow rate
        mass_flowrate = (P1 / (R * T1)) * self.inlet_area * velocity

        V6 = mass_flowrate * R * T6 / (P6 * self.exit_area)

        # print("V6 (should be 697)", V6)

        thrust = mass_flowrate * (V6 - velocity)

        # print("thrust (should be 43300", thrust)

        # unit: kW
        power = thrust * velocity / 1000

        # print("power (should be 8660kW)", int(power))

        # unit: kW
        heat_flowrate = mass_flowrate * (H4 - H3)

        # print("heat flowrate (should be 58309kW)", heat_flowrate)

        efficiency = power / heat_flowrate

        return Info(
            mass_flowrate=mass_flowrate,
            thrust=thrust,
            power=power,
            heat_flowrate=heat_flowrate,
            efficiency=efficiency,
        )


if __name__ == "__main__":
    j = Turbojet(0.6, 0.4, 50_000, 50_000, 9, 847 + 273, 30_000)
    print(j.calculate(273 - 33, 200).efficiency)
    # 14.9 percent (book), 14.3 percent (me)
    # good enough
