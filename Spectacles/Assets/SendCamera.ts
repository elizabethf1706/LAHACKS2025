@component
export class NewScript extends BaseScriptComponent {
    @input
    image: Image
    
    onAwake() {
    }

    private async sendCamera() {
        const texture = this.image.mainPass.baseTex;
        if (!texture) {
            print("Texture not found in the image component.");
            return;
        }

        const base64Image = await this.encodeTextureToBase64(texture);

        // TODO: send image
    }

    private encodeTextureToBase64(texture: Texture) {
        return new Promise((resolve, reject) => {
            Base64.encodeTextureAsync(
                texture,
                resolve,
                reject,
                CompressionQuality.LowQuality,
                EncodingType.Jpg
            );
        });
    }
}
