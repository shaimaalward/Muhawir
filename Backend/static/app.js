const micButton =
    document.getElementById("micButton");

const buttonText =
    document.getElementById("buttonText");

const statusText =
    document.getElementById("status");

const conversation =
    document.getElementById("conversation");


let mediaRecorder = null;

let audioChunks = [];

let recording = false;

let currentStream = null;

let mimeType = "";


// ======================================================
// MICROPHONE BUTTON
// ======================================================

micButton.addEventListener(
    "click",
    async () => {


        // ==================================================
        // START RECORDING
        // ==================================================

        if (!recording) {

            try {

                currentStream =
                    await navigator.mediaDevices
                        .getUserMedia({
                            audio: true
                        });


                const possibleTypes = [

                    "audio/webm;codecs=opus",

                    "audio/webm",

                    "audio/ogg;codecs=opus",

                    "audio/ogg",

                    "audio/mp4"

                ];


                mimeType =
                    possibleTypes.find(
                        type =>
                            MediaRecorder
                                .isTypeSupported(type)
                    ) || "";


                if (mimeType) {

                    mediaRecorder =
                        new MediaRecorder(
                            currentStream,
                            {
                                mimeType: mimeType
                            }
                        );

                }

                else {

                    mediaRecorder =
                        new MediaRecorder(
                            currentStream
                        );

                    mimeType =
                        mediaRecorder.mimeType;

                }


                console.log(
                    "Recording format:",
                    mimeType
                );


                audioChunks = [];


                mediaRecorder.ondataavailable =
                    event => {

                        if (event.data.size > 0) {

                            audioChunks.push(
                                event.data
                            );

                        }

                    };


                mediaRecorder.onstop =
                    sendAudio;


                mediaRecorder.start();


                recording = true;


                micButton.classList.add(
                    "recording"
                );


                buttonText.textContent =
                    "اضغط لإيقاف التسجيل";


                statusText.textContent =
                    "أستمع إليك...";

            }


            catch (error) {

                console.error(error);

                statusText.textContent =
                    "تعذر الوصول إلى الميكروفون.";

            }

        }


        // ==================================================
        // STOP RECORDING
        // ==================================================

        else {

            mediaRecorder.stop();


            recording = false;


            micButton.classList.remove(
                "recording"
            );


            buttonText.textContent =
                "اضغط للتحدث";


            statusText.textContent =
                "يفكر آدم...";

        }

    }
);



// ======================================================
// SEND AUDIO
// ======================================================

async function sendAudio() {


    let extension = "webm";


    if (mimeType.includes("ogg")) {

        extension = "ogg";

    }

    else if (mimeType.includes("mp4")) {

        extension = "mp4";

    }


    const audioBlob =
        new Blob(
            audioChunks,
            {
                type: mimeType
            }
        );


    console.log(
        "Audio type:",
        audioBlob.type
    );


    console.log(
        "Audio size:",
        audioBlob.size
    );


    // Completely stop microphone

    if (currentStream) {

        currentStream
            .getTracks()
            .forEach(
                track => track.stop()
            );

    }


    if (audioBlob.size === 0) {

        statusText.textContent =
            "لم يتم تسجيل صوت.";

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "audio",
        audioBlob,
        "recording." + extension
    );


    try {


        // ==================================================
        // SEND USER AUDIO TO MUHAWIR
        // ==================================================

        const response =
            await fetch(
                "/talk",
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server error: "
                + response.status
            );

        }


        const data =
            await response.json();


        // ==================================================
        // DISPLAY USER TRANSCRIPT
        // ==================================================

        const userMessage =
            document.createElement(
                "div"
            );


        userMessage.className =
            "user-message";


        userMessage.textContent =
            "أنت: "
            + data.user_text;


        conversation.appendChild(
            userMessage
        );


        // ==================================================
        // DISPLAY ADAM RESPONSE
        // ==================================================

        const adamMessage =
            document.createElement(
                "div"
            );


        adamMessage.className =
            "adam-message";


        adamMessage.textContent =
            "آدم: "
            + data.adam_text;


        conversation.appendChild(
            adamMessage
        );


        adamMessage.scrollIntoView({
            behavior: "smooth"
        });


        // ==================================================
        // PLAY ADAM'S REAL AI VOICE
        // ==================================================

        statusText.textContent =
            "آدم يتحدث...";


        playAdamVoice(
            data.adam_audio
        );

    }


    catch (error) {

        console.error(error);


        statusText.textContent =
            "حدث خطأ، حاول مرة أخرى.";

    }

}



// ======================================================
// PLAY OPENAI-GENERATED VOICE
// ======================================================

function playAdamVoice(
    base64Audio
) {


    const audio =
        new Audio(
            "data:audio/mp3;base64,"
            + base64Audio
        );


    audio.onended = () => {

        statusText.textContent =
            "يمكنك الرد الآن";

    };


    audio.onerror = () => {

        statusText.textContent =
            "تعذر تشغيل صوت آدم.";

    };


    audio.play();

}
