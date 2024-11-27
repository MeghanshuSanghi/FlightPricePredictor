document.addEventListener("DOMContentLoaded", () => {
    function validateInput(inputId, datalistId) {
        const input = document.getElementById(inputId);
        const datalist = document.getElementById(datalistId);
        const options = Array.from(datalist.options).map(option => option.value);

        input.addEventListener("blur", () => {
            if (!options.includes(input.value.trim())) {
                input.value = "";
                input.setCustomValidity("Please select a value from the list.");
            } else {
                input.setCustomValidity("");
            }
        });

        input.addEventListener("input", () => {
            if (options.includes(input.value.trim())) {
                input.setCustomValidity(""); 
            }
        });
    }

    validateInput("Source", "Source_list");

    validateInput("last_name", "dest_list");

    validateInput("third_name", "airline_list");

    validateInput("fifth_name", "stop_list");

    const dateInput = document.getElementById("_name");
    dateInput.addEventListener("blur", () => {
        const today = new Date();
        const selectedDate = new Date(dateInput.value);

        if (selectedDate < today) {
            dateInput.setCustomValidity("The date cannot be in the past.");
        } else {
            const maxDate = new Date(today);
            maxDate.setDate(today.getDate() + 60);
            if (selectedDate > maxDate) {
                dateInput.setCustomValidity("Please select a date within 60 days from today.");
            } else {
                dateInput.setCustomValidity("");
            }
        }
    });

        const sourceInput = document.getElementById("Source");
        const destinationInput = document.getElementById("last_name");

        sourceInput.addEventListener("blur", () => {
            if (sourceInput.value.trim() === destinationInput.value.trim() && sourceInput.value.trim() !== "") {
                sourceInput.setCustomValidity("Source and Destination cannot be the same.");
            } else {
                sourceInput.setCustomValidity("");
            }
        });
    
        destinationInput.addEventListener("blur", () => {
            if (sourceInput.value.trim() === destinationInput.value.trim() && destinationInput.value.trim() !== "") {
                destinationInput.setCustomValidity("Source and Destination cannot be the same.");
            } else {
                destinationInput.setCustomValidity("");
            }
            
        });
});
