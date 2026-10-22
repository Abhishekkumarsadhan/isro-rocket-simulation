import math

# ---------- Constants ----------
G = 6.674e-11
M_EARTH = 5.972e24
R_EARTH = 6371000.0

# ---------- Rocket stages (PSLV jaisa, simplified) ----------
stages = [
    {"name": "Stage 1", "dry": 30000, "fuel": 140000, "thrust": 5000000, "burn": 1500},
    {"name": "Stage 2", "dry": 6000,  "fuel": 40000,  "thrust": 800000,  "burn": 400},
    {"name": "Stage 3", "dry": 2500,  "fuel": 7500,   "thrust": 250000,  "burn": 80},
    {"name": "Stage 4", "dry": 1000,  "fuel": 2500,   "thrust": 60000,   "burn": 15},
]
payload = 1500   # satellite ka weight (kg)

def air_density(h):
    return 1.225 * math.exp(-h / 8500) if h < 100000 else 0.0

def gravity(h):
    return G * M_EARTH / (R_EARTH + h) ** 2

def pitch_angle(h):
    # 0 = seedha upar, 90 = zameen ke samanantar (gravity turn)
    if h < 1000:
        return 0
    return min(90, 90 * ((h - 1000) / 160000) ** 0.45)

# ---------- Initial state ----------
x, y = 0.0, 0.0
vx, vy = 0.0, 0.0
t, dt = 0.0, 0.5
cd, area = 0.3, 10.0

print("ISRO Rocket Launch Simulation")
print("=" * 56)
print("T(s)  Alt(km)  Speed(m/s)  Pitch  Stage")
print("-" * 56)

for i, s in enumerate(stages):
    fuel = s["fuel"]
    upper = sum(st["dry"] + st["fuel"] for st in stages[i + 1:]) + payload
    last_print = -10
    while fuel > 0:
        mass = s["dry"] + fuel + upper
        r = math.hypot(x, y + R_EARTH)
        h = r - R_EARTH
        speed = math.hypot(vx, vy)

        ang = math.radians(pitch_angle(h))
        thrust = s["thrust"]
        ax = thrust * math.sin(ang) / mass
        ay = thrust * math.cos(ang) / mass

        # drag velocity ke ulti direction mein
        if speed > 0:
            drag = 0.5 * air_density(h) * speed ** 2 * cd * area
            ax -= drag * (vx / speed) / mass
            ay -= drag * (vy / speed) / mass

        # gravity (zameen ke centre ki taraf)
        g = gravity(h)
        ax -= g * x / r
        ay -= g * (y + R_EARTH) / r

        vx += ax * dt; vy += ay * dt
        x += vx * dt;  y += vy * dt
        fuel -= s["burn"] * dt
        t += dt

        if t - last_print >= 10:
            print(f"{t:4.0f}  {h/1000:7.1f}  {speed:10.0f}  {math.degrees(ang):5.0f}  {s['name']}")
            last_print = t

    print(f">>> {s['name']} complete, separation!")

r = math.hypot(x, y + R_EARTH)
h = r - R_EARTH
speed = math.hypot(vx, vy)
orbital_v = math.sqrt(G * M_EARTH / r)

print("=" * 56)
print(f"Altitude: {h/1000:.1f} km | Speed: {speed:.0f} m/s | Needed: {orbital_v:.0f} m/s")

if speed >= orbital_v:
    print("SUCCESS! Satellite orbit mein pahunch gaya!")
else:
    print("FAIL! Speed kam thi, satellite wapas gir jayega.")