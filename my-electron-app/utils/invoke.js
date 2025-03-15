// const { exec } = require('child_process');

// function inviokeScript(scriptName, query, event) {
//     console.log(`Executing Python script: ${scriptName} with query: ${query}`);
//     exec(`python3 ${scriptName} "${query}"`, (error, stdout, stderr) => {
//         if (error) {
//             console.error(`Error executing Python script: ${stderr}`);
//             event.reply('query-response', `Error: ${stderr}`);
//             return;
//         }
//         console.log(`Python output: ${stdout}`);
//         event.reply('query-response', stdout.trim()); // Send response back to frontend
//     });
// }

// module.exports = { inviokeScript };

const { exec } = require('child_process');

function inviokeScript(scriptName, data, event) {
    const jsonData = JSON.stringify(data); // Convert data to JSON string
    console.log(`Executing Python script: ${scriptName} with data: ${jsonData}`);

    exec(`python3 helper/${scriptName} '${jsonData}'`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${stderr}`);
            event.reply('query-response', JSON.stringify({ error: stderr }));
            return;
        }
        console.log(`Python output: ${stdout}`);
        event.reply('query-response', stdout.trim()); // Send response back to frontend
    });
}

module.exports = { inviokeScript };
