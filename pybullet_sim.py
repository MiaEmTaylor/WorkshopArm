import pybullet as p
import time
import pybullet_data

class Testing():
    def __init__():
        physicsClient = p.connect(p.GUI)
        p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1,)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 1,)
        p.configureDebugVisualizer(p.COV_ENABLE_WIREFRAME, 1,)
        p.configureDebugVisualizer(p.COV_ENABLE_RGB_FRAMES, 1,)
        p.configureDebugVisualizer(p.COV_ENABLE_MOUSE_PICKING, 1,)
        p.setGravity(0, 0, -9.81)
        
    

# startPos = [0,0,1]
# startOrientation = p.getQuaternionFromEuler([0,0,0])
# boxId = p.loadURDF("r2d2.urdf",startPos, startOrientation)
#set the center of mass frame (loadURDF sets base link frame)
# startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos,
#startOrientation)
#for i in range (10000):
 #   p.stepSimulation()
 #   time.sleep(1./240.)
#cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
#print(cubePos,cubeOrn)
#p.disconnect()