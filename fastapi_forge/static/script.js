document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const projectName = document.getElementById("project_name").value;
        const usePostgres = document.getElementById("use_postgres").checked;
        const createDaos = document.getElementById("create_daos").checked;
        const createRoutes = document.getElementById("create_routes").checked;

        let models;
        try {
            models = JSON.parse(document.getElementById("models").value);
        } catch (e) {
            alert("Invalid JSON in models field");
            return;
        }

        const payload = {
            project_name: projectName,
            use_postgres: usePostgres,
            create_daos: createDaos,
            create_routes: createRoutes,
            models: models
        };

        try {
            const response = await fetch("http://localhost:9000/forge", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Success:", result);
            alert("Project configuration submitted successfully!");
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred while submitting the project configuration.");
        }
    });
});
