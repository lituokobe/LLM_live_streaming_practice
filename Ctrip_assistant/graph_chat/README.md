## Project Introduction ##
This is a chatbot that can help user to change flight, book hotel, book car rental and book excursion. There are 3 versions iterated along the development:
- In first_flowchart, all the tasks are handled by one agent with one universal tool.
- In second_flowchart, all the tasks are handled by one agent with 2 separate tools: safe tools (read database only) and sensitive tools (edit database).
- In third_flowchart, the tasks are received by the primary agent who will provide flight information and regular searches. 
The agent will assign the tasks to any of the 4 special agents: flight-change agent, hotel booking agent, car rental booking agent,
or excursion booking agent. The tools will also be separated to safe ones and sensitive ones.

Please be noted that, as third_flowchart requires stronger capability from AI model, 
my favorite gpt-4.1-nano will not perform well here. gpt-4o or above is more suitable for this version,
although it is more costly.