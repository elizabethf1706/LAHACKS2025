const GROQ_API_KEY = "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";

const remoteServiceModule = require("LensStudio:RemoteServiceModule");

@component
export class GroqProcessing extends BaseScriptComponent {
    @input
    private transcriptionTextComponent: Text;

    private prevText = "";
    private hasDone = false;

    onAwake() {
        this.createEvent("UpdateEvent").bind(this.update.bind(this));
    }

    private async update() {
        const curText = this.transcriptionTextComponent.text;

        if (this.prevText !== curText) {
            const body = {
                "model": "llama-3.1-8b-instant",
                "messages": [{
                    "role": "user",
                    "content": `This is some dialogue about a company. Reply with some useful information about this company.\n\n${curText}`
                }]
            };

            const headers = {
                "Content-Type": "application/json",
                Authorization: `Bearer ${GROQ_API_KEY}`
            };

            // const request = new Request("https://api.groq.com/openai/v1/chat/completions", {
            //     method: "POST",
            //     headers,
            //     body: JSON.stringify(body),
            // });

            // const response = await remoteServiceModule.fetch(request);
                
            // const responseText = response.choices[0].message.content;
            // if (responseText.toLowerCase() === "yes") {
            //     // something here
            // } else {
            //     // something else here
            // }

            print("text changed! ");
        }

        this.prevText = curText;
    }
}
