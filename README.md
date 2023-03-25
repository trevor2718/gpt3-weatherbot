# gpt3-weatherbot

## Frist Task 
We have a number of custom APIs and data services that relate to weather and the environment, including historical data as well as proprietary forecast data.

We want to integrate a GPT-3 (or GPT-4) API with our proprietary data in order to allow customers to access and analyze our data through a natural language interaction model. So probably need experience in Natural Language models and custom data integration. Please make sure if these skills are in your wheelhouse.

So the objective here would be to demonstrate knowledge and capabilities of GPT-4. We'd set you up with developer access to our APIs, and we'd want you to write up a first-round prototype chatbot that is capable of answering two questions.

1. "Do I have time to go for a walk before it rains?" - this one will have some context that we'll fudge (give you a fixed lat/lon location), and it also requires some inferences from a chatbot to understand the context. It would access our nowcast API to get the hyper-local, hyper-accurate prediction on rain probability and answer the question in a natural-language format.

2. "What is the weather in Orlando, FL tomorrow?" - This one is just a good demonstration of the most basic functionality, the ability to get the data points from the API and then figure out how to format them in a way that a user might expect from in a natural-language response.

This demonstrates:
1. access to our internal APIs,
2. the ability to parse the responses into natural language,
3. the ability to provide contextual information about the user and see how well the chatbot infers the rest in the formation of its response.

This is the API you'll access, documentation should be there:
https://myradar.dev/api-details#api=forecast-api&operation=get-forecast-latitude-longitude 

The "nowcast" data that you will use for the first question is in the "minutely" section of the response!

Please let me know if you have any questions.
