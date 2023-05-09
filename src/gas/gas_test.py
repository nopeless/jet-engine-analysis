from gas import Gas


Th = 600
Tc = 300

# 20 atm
P1 = 20 * 100_000
# 1 atm
P3 = 1 * 100_000

# It is usually better to calculate the required pressure first
# as it is most likely to be the limiting factor of the engine

# Using pressure, it is possible to derive all 4 volumes and the other 2 pressures

# 1 -> 4 (adiabatic)
air_1 = Gas(P=P1, T=Th)
V1 = air_1.V
air_1.T = Tc
P4 = air_1.P
V4 = air_1.V

# 3 -> 2 (adiabatic)
air_3 = Gas(P=P3, T=Tc)
V3 = air_3.V
air_3.T = Th
P2 = air_3.P
V2 = air_3.V

# Plotting these points will show the carnot cycle diagram
points = [
    (V1, P1, Th),
    (V2, P2, Th),
    (V3, P3, Tc),
    (V4, P4, Tc),
]

print("=" * 80)
for v, p, t in points:
    print(f"{v * 1000:.1f}L {p / 100_000:.1f}bar {t:.1f}K")
print("=" * 80)


print(f"Th: {Th}K, Tc: {Tc}K")

# 1
air = Gas(V=V1, P=P1)
print(f"{air}")

# 1->2
print("starting isothermal expansion")
air.lock("T")
air.V = V2  # Piston moves
print(air)
print(f"Entropy change: {air.dS}")
Qh = air.dW

# 2->3
print("starting adiabatic compression")
air.unlock()
air.V = V3  # Piston moves
print(air)
print(f"Entropy change: {air.dS}")
W_23 = air.dW

# 3->4
print("starting isothermal compression")
air.lock("T")
air.V = V4  # Piston moves
print(air)
print(f"Entropy change: {air.dS}")
Qc = -air.dW

# 4->1
print("starting adiabatic expansion")
air.unlock()
air.V = V1  # Piston moves
print(air)
print(f"Entropy change: {air.dS}")
W_41 = air.dW

print(f"Total work done 2->3 and 4->1: {W_23 + W_41:.1f}")

print(f"Total entropy: {air.S:.1f}")
print(f"Total work: {air.W:.1f}")
print(f"Total heat in: {Qh:.1f}")
print(f"Total heat out: {Qc:.1f}")
print("Efficiency using (W/Qh): ", air.W / Qh)
print("Efficiency using (1 - Qc/Qh): ", 1 - Qc / Qh)
print("Efficiency using (1 - Tc/Th): ", 1 - Tc / Th)

print("--- The bottom 3 lines should have equal values ---")
