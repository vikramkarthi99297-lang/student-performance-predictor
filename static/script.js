const form =
    document.getElementById(
        "predictionForm"
    );


if (form) {


    const predictButton =
        document.getElementById(
            "predictButton"
        );


    const clearButton =
        document.getElementById(
            "clearButton"
        );


    const resultText =
        document.getElementById(
            "resultText"
        );


    const studentResult =
        document.getElementById(
            "studentResult"
        );


    const passProbability =
        document.getElementById(
            "passProbability"
        );


    const failProbability =
        document.getElementById(
            "failProbability"
        );


    const passProgress =
        document.getElementById(
            "passProgress"
        );


    const failProgress =
        document.getElementById(
            "failProgress"
        );


    // =========================================
    // SUBMIT
    // =========================================

    form.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            predictButton.disabled =
                true;


            predictButton.innerText =
                "Predicting...";


            const formData =
                new FormData(form);


            try {

                const response =
                    await fetch(
                        "/predict",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!data.success) {

                    alert(
                        data.message
                    );

                    return;

                }


                // Result

                resultText.innerText =
                    data.prediction;


                resultText.classList.remove(
                    "result-pass",
                    "result-fail"
                );


                if (
                    data.prediction ===
                    "Pass"
                ) {

                    resultText.classList.add(
                        "result-pass"
                    );

                }

                else {

                    resultText.classList.add(
                        "result-fail"
                    );

                }


                studentResult.innerText =
                    "Prediction for " +
                    data.student_name;


                // Probability

                const pass =
                    data.probabilities.Pass ||
                    0;


                const fail =
                    data.probabilities.Fail ||
                    0;


                passProbability.innerText =
                    pass + "%";


                failProbability.innerText =
                    fail + "%";


                passProgress.style.width =
                    pass + "%";


                failProgress.style.width =
                    fail + "%";


            }


            catch (error) {

                console.error(error);


                alert(
                    "Unable to connect to server."
                );

            }


            finally {

                predictButton.disabled =
                    false;


                predictButton.innerText =
                    "Predict Performance";

            }

        }

    );


    // =========================================
    // CLEAR
    // =========================================

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function() {

                form.reset();


                resultText.innerText =
                    "Waiting...";


                resultText.classList.remove(
                    "result-pass",
                    "result-fail"
                );


                studentResult.innerText =
                    "Enter details and click predict.";


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

    }

}