//@input float distance = 0.5                          // world-units in front of camera
//@input Component.Camera camera                       // drag your Orthographic or Main Camera here

function onUpdate() {
    var camTrans = script.camera.getTransform();
    var forward  = camTrans.forward;                    // unit-vector forward
    var target   = camTrans.getWorldPosition().add(forward.uniformScale(script.distance));
    script.getSceneObject().getTransform().setWorldPosition(target);
  }
  
  script.createEvent("UpdateEvent").bind(onUpdate);
  