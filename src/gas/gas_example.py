from gas import Gas

Th = 600
Tc = 300

# 20 atm
P1 = 20 * 100_000
# 1 atm
P3 = 1 * 100_000

# precalculating required volumes
air_1 = Gas(P=P1, T=Th)
V1 = air_1.V
air_1.T = Tc
V4 = air_1.V

air_3 = Gas(P=P3, T=Tc)
V3 = air_3.V
air_3.T = Th
V2 = air_3.V

print(f"Th: {Th}K, Tc: {Tc}K")

# 1
air = Gas(V=V1, P=P1)

# 1->2
air.lock("T")
air.V = V2  # Piston moves
Qh = air.dW

# 2->3
air.unlock()
air.V = V3  # Piston moves
W_23 = air.dW

# 3->4
air.lock("T")
air.V = V4  # Piston moves
Qc = -air.dW

# 4->1
air.unlock()
air.V = V1  # Piston moves
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
