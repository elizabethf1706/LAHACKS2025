@component
export class NewScript extends BaseScriptComponent {
    @input
    private transcriptionTextComponent: Text;

    private prevText = "";

    onAwake() {
        this.createEvent("UpdateEvent").bind(this.update.bind(this));
    }

    private update() {
        const curText = this.transcriptionTextComponent.text;

        if (this.prevText !== curText) {
            // TODO: replace with actual Groq request
            print("text changed!");
        }
    }
}
