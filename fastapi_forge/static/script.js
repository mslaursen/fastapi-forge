document.addEventListener("DOMContentLoaded", () => {
    const generateButton = document.getElementById("generateButton");
    const shutdownButton = document.getElementById("shutdownButton");
    const responseOutput = document.getElementById("responseOutput");

    const makeRequest = async (url, options, successMessage) => {
        try {
            const response = await fetch(url, options);

            if (response.ok) {
                const data = successMessage ? successMessage : await response.json();
                responseOutput.textContent = `Response: ${JSON.stringify(data)}`;
            } else {
                responseOutput.textContent = `Error: ${response.status} - ${response.statusText}`;
            }
        } catch (error) {
            responseOutput.textContent = `Request failed: ${error.message}`;
        }
    };

    if (generateButton) {
        generateButton.addEventListener("click", () => {
            makeRequest("http://localhost:8000/forge", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(
                    {
                        project_name: "temp_project8",
                        use_postgres: true,
                        create_daos: true,
                        create_endpoints: true,
                    }
                ),
            });
        });
    } else {
        console.error("Generate button not found!");
    }

    if (shutdownButton) {

        shutdownButton.addEventListener("click", () => {
            makeRequest("http://localhost:8000/shutdown", { method: "POST" }, "Server shutdown");
        });
    } else {
        console.error("Shutdown button not found!");
    }
});
