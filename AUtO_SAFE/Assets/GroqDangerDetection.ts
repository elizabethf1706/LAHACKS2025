const GROQ_API_KEY = "api key here";

const remoteServiceModule = require("LensStudio:RemoteServiceModule");

@component
export class NewScript extends BaseScriptComponent {
    @input
    private transcriptionTextComponent: Text;

    private prevText = "";

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
                    "content": `Does this dialogue signal potential danger? Answer only "yes" or "no", with no other output.\n\n${curText}`
                }]
            };

            const headers = {
                "Content-Type": "application/json",
                Authorization: `Bearer ${GROQ_API_KEY}`
            };

            // const request = new Request("https://api.openai.com/v1/chat/completions", {
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

            print("text changed!");
        }

        this.prevText = curText;
    }
}
