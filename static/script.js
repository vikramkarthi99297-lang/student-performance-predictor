// =====================================================
// GET HTML ELEMENTS
// =====================================================

const form =
    document.getElementById("predictionForm");

const predictButton =
    document.getElementById("predictButton");

const clearButton =
    document.getElementById("clearButton");

const resultText =
    document.getElementById("resultText");

const passProbability =
    document.getElementById("passProbability");

const failProbability =
    document.getElementById("failProbability");

const passProgress =
    document.getElementById("passProgress");

const failProgress =
    document.getElementById("failProgress");



// =====================================================
// FORM SUBMIT
// =====================================================

form.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        // ---------------------------------------------
        // CHANGE BUTTON
        // ---------------------------------------------

        predictButton.disabled = true;

        predictButton.innerText =
            "Predicting...";


        // ---------------------------------------------
        // GET FORM DATA
        // ---------------------------------------------

        const formData =
            new FormData(form);


        try {

            // -----------------------------------------
            // SEND DATA TO PYTHON BACKEND
            // -----------------------------------------

            const response =
                await fetch(
                    "/predict",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            // -----------------------------------------
            // GET RESPONSE
            // -----------------------------------------

            const data =
                await response.json();


            // -----------------------------------------
            // CHECK SUCCESS
            // -----------------------------------------

            if (!data.success) {

                alert(data.message);

                return;

            }


            // -----------------------------------------
            // GET PREDICTION
            // -----------------------------------------

            const prediction =
                data.prediction;


            // -----------------------------------------
            // DISPLAY RESULT
            // -----------------------------------------

            resultText.innerText =
                prediction;


            // Remove previous classes

            resultText.classList.remove(
                "result-pass",
                "result-fail"
            );


            // Add correct class

            if (prediction === "Pass") {

                resultText.classList.add(
                    "result-pass"
                );

            } else {

                resultText.classList.add(
                    "result-fail"
                );

            }


            // -----------------------------------------
            // GET PROBABILITY
            // -----------------------------------------

            const probabilities =
                data.probabilities;


            const pass =
                probabilities.Pass || 0;

            const fail =
                probabilities.Fail || 0;


            // -----------------------------------------
            // DISPLAY PROBABILITY
            // -----------------------------------------

            passProbability.innerText =
                pass + "%";


            failProbability.innerText =
                fail + "%";


            // -----------------------------------------
            // PROGRESS BARS
            // -----------------------------------------

            passProgress.style.width =
                pass + "%";


            failProgress.style.width =
                fail + "%";


        }

        catch (error) {

            console.error(error);

            alert(
                "Unable to connect to the server."
            );

        }

        finally {

            predictButton.disabled = false;

            predictButton.innerText =
                "Predict Performance";

        }

    }
);



// =====================================================
// CLEAR BUTTON
// =====================================================

clearButton.addEventListener(
    "click",
    function() {


        // Clear form

        form.reset();


        // Reset result

        resultText.innerText =
            "Waiting for prediction...";


        resultText.classList.remove(
            "result-pass",
            "result-fail"
        );


        // Reset probabilities

        passProbability.innerText =
            "0%";


        failProbability.innerText =
            "0%";


        passProgress.style.width =
            "0%";


        failProgress.style.width =
            "0%";

    }
);