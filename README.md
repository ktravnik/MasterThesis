# Manual for the included generator

## Libraries that need to be installed:
- psutil (pip install psutil)
- request (pip install request)

## Adding a script to the generator
- Create the $nameofscript.json file and save it in the scripts folder.
- Describing all the necessary parameters in the created $nameofscript.json file according to the json template described below (you can be inspired by the already created jsons or by the sample.json template)
 
```json
{
"description",
"detail_description": "Script description(string)",
    "params": [
        {
            "label": "Label name(string)",
            "description": "label description(string)",
            "prefix": "parameter used when running the script(string)",
            "type": "type of widget to use",
            "required": "whether the parameter is required for the script to work properly(boolean)",
	    "default": "pre-populated value in the created field"
        },
	...
```	
 - Running the main.py class either in the development environment or using ./main.py in a dedicated folder
 - Verifying that the json generator is found, read and displayed (error messages)
 - If the following steps take place, the script is successfully added and you can use all the functionality the generator has.

## Initializing bots
- Define the available bots via the configuration.json file in the format below, with each field containing first the slave ip address followed by the port. This file is loaded by the main class, which fills the created combobox with all the bots found, (here the program is thought of in two ways, either the program will believe that the user has specified live and active machines or it will use a mechanism that props all the specified bots - the problem here arises because of the timeout, where the response from one machine comes in 5 seconds on average therefore if an attack was simulated for say 10 bots, it would take more than 50 seconds to verify)

```json
"agent_list": [
		[
			"localhost",
			10050
		],
		[
			"localhost",
			10051
		]
	],
	"local_port": 10050
}
```
	
- Once the bots are loaded in the main program, you need to enable the ./agent.py script on each bot, which then starts listening on the set port and waits as soon as it receives instructions from the master.

## Enabling attacks
- If everything is ready, the user first selects the attack, sets its parameters, then selects how many bots should be used for the attack (1 - the maximum number of bots, always starting from the first one created in the configuration file.) and then selects other information for the statistics required for the test. Last but not least, the user can specify the address of the probe on a given server, which allows to check if the target of the attack matches and to get additional data. The test is then turned on using "Run the script".
- Next, the user either waits for the test to finish or interrupts it manually using the "Interrupt the scripts" button. He is informed about all the run information in the Bots list frame.
- After the attack is finished, statistics are generated in a dedicated results folder and the user is asked if he wants to view them immediately.
- Finally, he can export the parameters or import new parameters and run the test again.
