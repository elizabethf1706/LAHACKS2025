

@component
export class ButtonHandler extends BaseScriptComponent {
    @input
    private pfp1: SceneObject;

    @input
    private pfp2: SceneObject;

    @input
    private pfp3: SceneObject;

    @input
    private loading: SceneObject;

    @input
    private linkInfoTextObj: Text;

    onCreate() {
        // expose our handler so PinchButton can invoke it
        this.api.onButtonPressed = this.onButtonPressed.bind(this);
    }

    onButtonPressed() {
        // debug-print so we know it fired
        // print("🔥 onButtonPressed() fired!");

        // hide all three buttons
        this.pfp1.enabled = false;
        this.pfp2.enabled = false;
        this.pfp3.enabled = false;

        // update the LinkD Info text
        this.linkInfoTextObj.enabled = false;

        // wait to find loading
        this.loading.enabled = true;
        // getDataFromOtherSource();

        //this.loading.enabled = false;



        // Reveal text
        this.linkInfoTextObj.enabled = true;

        // Update text
        const txtA = this.linkInfoTextObj;
        if (txtA) {
            txtA.text = "PFP1 was pressed";
          return;
        }
    }
} 

