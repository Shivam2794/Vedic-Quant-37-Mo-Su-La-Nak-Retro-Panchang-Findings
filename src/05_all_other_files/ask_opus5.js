import { OpenRouter } from "@openrouter/sdk";
import fs from 'fs';

const openrouter = new OpenRouter({
  apiKey: "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"
});

async function main() {
  const prompt = fs.readFileSync('opus5_prompt.txt', 'utf8');

  try {
    const stream = await openrouter.chat.send({
      chatRequest: {
        model: "anthropic/claude-opus-5", // user specifically requested this
        messages: [
          {
            role: "user",
            content: prompt
          }
        ],
        stream: true
      }
    });

    let response = "";
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        response += content;
        process.stdout.write(content);
      }

      if (chunk.usage) {
        console.log("\nReasoning tokens:", chunk.usage.completionTokensDetails?.reasoningTokens);
      }
    }
  } catch (error) {
    console.error("Error calling OpenRouter:", error.message);
  }
}

main();
