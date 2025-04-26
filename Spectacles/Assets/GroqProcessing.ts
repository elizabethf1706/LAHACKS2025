const GROQ_API_KEY = "";

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

    private update() {
        const curText = this.transcriptionTextComponent.text;

        if (this.prevText !== curText) {
            this.getInfo(curText);

            print("text changed! " + this.prevText + " | " + curText);

            this.prevText = curText;
        }

        
    }

    private async getInfo(text: string) {
        const body = {
            "model": "llama-3.1-8b-instant",
            "messages": [{
                "role": "user",
                "content": `This is some dialogue about a company. Reply with some useful information about this company.\n\n${text}`
            }]
        };

        const headers = {
            "Content-Type": "application/json",
            Authorization: `Bearer ${GROQ_API_KEY}`
        };

        const request = new Request("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers,
            body: JSON.stringify(body),
        });

        const response = await remoteServiceModule.fetch(request);
        const responseJson = await response.json();
            
        const responseText = responseJson.choices[0].message.content;

        print(responseText);
    }
}
