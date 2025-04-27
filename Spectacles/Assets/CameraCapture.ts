let cameraModule = require('LensStudio:CameraModule');

@component
export class CameraCapture extends BaseScriptComponent {
    @input
    image: Image

    private cameraRequest: CameraModule.CameraRequest;
    private cameraTexture: Texture;
    private cameraTextureProvider: CameraTextureProvider;
    
    onAwake() {
        this.createEvent("OnEnableEvent").bind(this.startRecording);
        print("???");
    }

    private updateFrame(cameraFrame: CameraFrame) {
        print(this.image);
        if (this.image) {
            print("?????");
            this.image.mainPass.baseTex = this.cameraTexture;
        }
    }

    private startRecording() {
        print("????");
        print(this.image)
        this.cameraRequest = CameraModule.createCameraRequest();
        this.cameraRequest.cameraId = CameraModule.CameraId.Default_Color;

        this.cameraTexture = cameraModule.requestCamera(this.cameraRequest);
        this.cameraTextureProvider = this.cameraTexture.control as CameraTextureProvider;

        this.cameraTextureProvider.onNewFrame.add((frame) => this.updateFrame(frame));
    }
}
