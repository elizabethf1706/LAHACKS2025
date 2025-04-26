const remoteServiceModule = require("LensStudio:RemoteServiceModule");

@component
export class GroqProcessing extends BaseScriptComponent {
    @input
    private transcriptionTextComponent: Text;

    @input
    private outputTextComponent: Text;

    private prevText = "";
    private hasDone = false;

    onAwake() {
        this.createEvent("UpdateEvent").bind(this.update.bind(this));
    }

    private update() {
        // const curText = this.transcriptionTextComponent.text;

        // if (this.prevText !== curText) {
        //     this.getInfo(curText);

        //     print("text changed! " + this.prevText + " | " + curText);

        //     this.prevText = curText;
        // }

        
    }

    private async getInfo(text: string) {
    //     const body = {
    //         "model": "llama-3.3-70b-versatile",
    //         "messages": [
    //             {
    //                 "role": "system",
    //                 "content": "You are a personal assistant helping a user at a career fair. You are given some dialogue from the user and the person they're speaking to; the user messages are *not* talking to you, they're transcripts of the user's conversation with someone else. Reply with information that may help the user in this conversation. If you cannot provide direct help, don't say anything."
    //             },
    //             {
    //                 "role": "user",
    //                 "content": text
    //             }
    //         ]
    //     };

    //     const headers = {
    //         "Content-Type": "application/json",
    //     };

    //     const request = new Request("https://api.groq.com/openai/v1/chat/completions", {
    //         method: "POST",
    //         headers,
    //         body: JSON.stringify(body),
    //     });

    //     const response = await remoteServiceModule.fetch(request);
    //     const responseJson = await response.json();
            
    //     const responseText = responseJson.choices[0].message.content;

    //     this.outputTextComponent.text = responseText;
    //     print("hey");
    }
}
