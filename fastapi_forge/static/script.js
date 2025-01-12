document.addEventListener("DOMContentLoaded", () => {
    const generateButton = document.getElementById("generateButton");
    const responseOutput = document.getElementById("responseOutput");

    generateButton.addEventListener("click", async () => {
        try {
            const response = await fetch("http://localhost:8000/forge", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ project_name: "temp_project" }),
            });

            if (response.ok) {
                const data = await response.json();
                responseOutput.textContent = `Response: ${JSON.stringify(data)}`;
            } else {
                responseOutput.textContent = `Error: ${response.statusText}`;
            }
        } catch (error) {
            responseOutput.textContent = `Request failed: ${error.message}`;
        }
    });
});
