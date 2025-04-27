// @input Component.MaterialMeshVisual loadingMesh
// @input float startValue = 1;  {"widget":"slider", "min":0, "max":1, "step":0.1}

var PercentageController = function (matMeshVisual) {
    this.mat = matMeshVisual.mainMaterial.clone();
    matMeshVisual.mainMaterial = this.mat;
    this.pass = this.mat.mainPass;
}

PercentageController.prototype.update = function (value) {
    this.pass.progress_value = value;
}

if (!script.loadingMesh){
    print("No loading mesh added to 3DLoadingIndicator! Please add a mesh with a loading material");
} 
var ctrl = new PercentageController(script.loadingMesh);
ctrl.update(script.startValue);

// API to set the progress of this indicator. Input is number 0 -> 1
// Eg. script.api.setProgress(0.6);
script.api.setProgress = ctrl.update.bind(ctrl);
