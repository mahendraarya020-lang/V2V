import sys, os
sys.path.insert(0, os.path.abspath('backend'))
from app import simulation_engine
from core.vehicle import Vehicle

# Setup
simulation_engine.running = True
simulation_engine.time_elapsed = 0.0

# Create simple platoon P0 with 4 vehicles
v0 = Vehicle(0, 0); v0.is_leader = True; v0.position = 100; v0.velocity = 20
v1 = Vehicle(1, 0); v1.position = 80; v1.velocity = 20
v2 = Vehicle(2, 0); v2.position = 60; v2.velocity = 20
v3 = Vehicle(3, 0); v3.position = 40; v3.velocity = 20
simulation_engine.vehicles = [v0, v1, v2, v3]

# Let it run for 1 second to stabilize
for _ in range(100): simulation_engine.step()

# Trigger transfer V1 to P1 (doesn't exist, but let's make P1)
p1_v4 = Vehicle(4, 1); p1_v4.is_leader = True; p1_v4.position = 50; p1_v4.velocity = 20
simulation_engine.vehicles.append(p1_v4)

print('--- Before Transfer ---')
for v in [v0, v1, v2]: print(f'V{v.id}: pos={v.position:.1f}, vel={v.velocity:.1f}, acc={v.acceleration:.1f}, mode={v.control_mode}, gap={v0.position - v.position if v.id==1 else (v1.position - v.position if v.id==2 else 0):.1f}')

res = simulation_engine.transfer_vehicle(1, 1)
print(f'Transfer result: {res}')

print('--- During DEPARTING ---')
for _ in range(150): # 1.5 seconds
    simulation_engine.step()
for v in [v0, v1, v2]: print(f'V{v.id}: pos={v.position:.1f}, vel={v.velocity:.1f}, acc={v.acceleration:.1f}, mode={v.control_mode}, pred={v.last_leader_data["position"] if v.last_leader_data else "None":.1f}')

print('--- After DEPARTING (V1 in IN_TRANSIT) ---')
for _ in range(200): # 2.0 seconds
    simulation_engine.step()
    if _ % 50 == 0:
        print(f' t={(1.5 + _/100.0):.1f}s -> V2: pos={v2.position:.1f}, vel={v2.velocity:.1f}, acc={v2.acceleration:.1f}, mode={v2.control_mode}, pred_id={'Unknown'}, target_gap_to_v0={v0.position - v2.position - v2.length:.1f}')

