const API_URL = "http://127.0.0.1:8501/ask-services";
const SYSTEM_STATS_URL = "/system-stats";
const MODEL_STATUS_URL = "/model-status";


const navItems = document.querySelectorAll(".nav-item");
const sections = document.querySelectorAll(".section");


const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const clearChatButton =
    document.getElementById("clearChat");

const modelSelect =
    document.getElementById("modelSelect");

const chatMessages =
    document.getElementById("chatMessages");


/* =========================================================
   NAVIGATION
   ========================================================= */

navItems.forEach((item) => {

    item.addEventListener("click", () => {

        const targetSection =
            item.dataset.section;


        navItems.forEach((nav) => {
            nav.classList.remove("active");
        });


        item.classList.add("active");


        sections.forEach((section) => {
            section.classList.remove("active-section");
        });


        const selectedSection =
            document.getElementById(targetSection);


        if (selectedSection) {
            selectedSection.classList.add(
                "active-section"
            );
        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    });

});


/* =========================================================
   CHAT STORAGE
   ========================================================= */

let conversation = [];


function saveConversation() {

    localStorage.setItem(
        "hybrid_llm_conversation",
        JSON.stringify(conversation)
    );

}


function loadConversation() {

    const saved =
        localStorage.getItem(
            "hybrid_llm_conversation"
        );


    if (!saved) {
        return;
    }


    try {

        conversation =
            JSON.parse(saved);


        conversation.forEach((message) => {

            renderMessage(
                message.role,
                message.content,
                message.source,
                message.similarity
            );

        });


    } catch (error) {

        console.error(
            "Could not load saved conversation:",
            error
        );


        conversation = [];

    }

}


/* =========================================================
   MESSAGE RENDERING
   ========================================================= */

function removeEmptyState() {

    const emptyChat =
        chatMessages.querySelector(
            ".empty-chat"
        );


    if (emptyChat) {
        emptyChat.remove();
    }

}


function renderMessage(
    role,
    content,
    source = null,
    similarity = null
) {

    removeEmptyState();


    const message =
        document.createElement("div");


    message.className =
        `message ${role}`;


    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        role === "user"
            ? "👤"
            : "🤖";


    const messageContent =
        document.createElement("div");


    messageContent.className =
        "message-content";


    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    bubble.textContent =
        content;


    messageContent.appendChild(
        bubble
    );


    if (
        role === "assistant" &&
        source
    ) {

        const meta =
            document.createElement("div");


        meta.className =
            "message-meta";


        const sourceBadge =
            document.createElement("span");


        sourceBadge.className =
            "source-badge";


        sourceBadge.textContent =
            `📄 ${source}`;


        const similarityBadge =
            document.createElement("span");


        similarityBadge.textContent =
            `🔍 Similarity: ${Number(
                similarity
            ).toFixed(4)}`;


        meta.appendChild(
            sourceBadge
        );


        meta.appendChild(
            similarityBadge
        );


        messageContent.appendChild(
            meta
        );

    }


    message.appendChild(
        avatar
    );


    message.appendChild(
        messageContent
    );


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* =========================================================
   STREAMING MESSAGE
   ========================================================= */

function createStreamingMessage() {

    removeEmptyState();


    const message =
        document.createElement("div");


    message.className =
        "message assistant";


    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        "🤖";


    const messageContent =
        document.createElement("div");


    messageContent.className =
        "message-content";


    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    bubble.textContent =
        "";


    messageContent.appendChild(
        bubble
    );


    message.appendChild(
        avatar
    );


    message.appendChild(
        messageContent
    );


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return bubble;

}


/* =========================================================
   LOADING MESSAGE
   ========================================================= */

function showLoadingMessage() {

    removeEmptyState();


    const message =
        document.createElement("div");


    message.className =
        "message assistant";


    message.id =
        "loadingMessage";


    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        "🤖";


    const content =
        document.createElement("div");


    content.className =
        "message-content";


    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    const typing =
        document.createElement("div");


    typing.className =
        "typing";


    for (let i = 0; i < 3; i++) {

        const dot =
            document.createElement("span");


        typing.appendChild(dot);

    }


    bubble.appendChild(
        typing
    );


    content.appendChild(
        bubble
    );


    message.appendChild(
        avatar
    );


    message.appendChild(
        content
    );


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


function removeLoadingMessage() {

    const loading =
        document.getElementById(
            "loadingMessage"
        );


    if (loading) {
        loading.remove();
    }

}


/* =========================================================
   SEND QUESTION
   ========================================================= */

async function askQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        questionInput.focus();

        return;
    }


    const selectedModel =
        modelSelect.value;


    renderMessage(
        "user",
        question
    );


    conversation.push({
        role: "user",
        content: question
    });


    saveConversation();


    questionInput.value = "";

    questionInput.style.height =
        "auto";


    sendButton.disabled =
        true;


    showLoadingMessage();


    try {

        const response =
            await fetch(
                `${API_URL}?question=${encodeURIComponent(
                    question
                )}&model=${encodeURIComponent(
                    selectedModel
                )}`,
                {
                    method: "GET"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Backend returned HTTP ${response.status}`
            );

        }


        if (!response.body) {

            throw new Error(
                "Streaming is not supported by this browser."
            );

        }


        removeLoadingMessage();


        const answerBubble =
            createStreamingMessage();


        let answer = "";


        const reader =
            response.body.getReader();


        const decoder =
            new TextDecoder();


        while (true) {

            const {
                value,
                done
            } =
                await reader.read();


            if (done) {
                break;
            }


            const chunk =
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );


            answer += chunk;


            answerBubble.textContent =
                answer;


            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        }


        const finalChunk =
            decoder.decode();


        if (finalChunk) {

            answer += finalChunk;


            answerBubble.textContent =
                answer;

        }


        if (!answer.trim()) {

            answer =
                "No answer was returned by the backend.";


            answerBubble.textContent =
                answer;

        }


        conversation.push({
            role: "assistant",
            content: answer
        });


        saveConversation();


    } catch (error) {

        removeLoadingMessage();


        const errorMessage =
            `Unable to connect to the assistant backend.\n\n${error.message}`;


        renderMessage(
            "assistant",
            errorMessage
        );


        conversation.push({
            role: "assistant",
            content: errorMessage
        });


        saveConversation();


        console.error(
            "Assistant request failed:",
            error
        );

    } finally {

        sendButton.disabled =
            false;


        questionInput.focus();

    }

}


/* =========================================================
   CLEAR CHAT
   ========================================================= */

clearChatButton.addEventListener(
    "click",
    () => {

        conversation = [];


        localStorage.removeItem(
            "hybrid_llm_conversation"
        );


        chatMessages.innerHTML = `
            <div class="empty-chat">

                <div class="empty-icon">
                    💬
                </div>

                <div class="empty-title">
                    Start a conversation
                </div>

                <div class="empty-description">
                    Ask something about autoscaling,
                    Kubernetes, HPA, KEDA, Redis,
                    or the other documents in your
                    knowledge base.
                </div>

            </div>
        `;


        questionInput.focus();

    }
);


/* =========================================================
   TEXTAREA AUTO-RESIZE
   ========================================================= */

questionInput.addEventListener(
    "input",
    () => {

        questionInput.style.height =
            "auto";


        questionInput.style.height =
            `${Math.min(
                questionInput.scrollHeight,
                130
            )}px`;

    }
);


/* =========================================================
   ENTER TO SEND
   ========================================================= */

questionInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();


            if (!sendButton.disabled) {
                askQuestion();
            }

        }

    }
);


/* =========================================================
   SEND BUTTON
   ========================================================= */

sendButton.addEventListener(
    "click",
    askQuestion
);


/* =========================================================
   LIVE SYSTEM STATISTICS
   ========================================================= */

function updateElement(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {
        element.textContent = value;
    }

}


async function updateSystemStats() {

    try {

        const response =
            await fetch(
                SYSTEM_STATS_URL,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                `System stats returned HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        const memory =
            data.memory;


        const swap =
            data.swap;


        updateElement(
            "cpuUsage",
            `${data.cpu_percent.toFixed(1)}%`
        );


        updateElement(
            "ramUsage",
            `${memory.percent.toFixed(1)}%`
        );


        updateElement(
            "ramUsed",
            `${memory.used_gb.toFixed(2)} GB`
        );


        updateElement(
            "ramAvailable",
            `${memory.available_gb.toFixed(2)} GB`
        );


        updateElement(
            "ramTotal",
            `${memory.total_gb.toFixed(2)} GB`
        );


        updateElement(
            "swapUsage",
            `${swap.percent.toFixed(1)}%`
        );


        updateElement(
            "swapUsed",
            `${swap.used_gb.toFixed(2)} GB`
        );


        const status =
            document.getElementById(
                "systemStatsStatus"
            );


        if (status) {

            status.textContent =
                "Live";


            status.classList.add(
                "connected"
            );

        }


    } catch (error) {

        console.error(
            "Could not update system statistics:",
            error
        );


        const status =
            document.getElementById(
                "systemStatsStatus"
            );


        if (status) {

            status.textContent =
                "Offline";


            status.classList.remove(
                "connected"
            );

        }

    }

}


/* =========================================================
   MODEL RUNTIME MONITORING
   ========================================================= */

function setModelStep(
    activeStep
) {

    const steps = {
        unload: document.getElementById(
            "modelStepUnload"
        ),

        load: document.getElementById(
            "modelStepLoad"
        ),

        ready: document.getElementById(
            "modelStepReady"
        ),

        generate: document.getElementById(
            "modelStepGenerate"
        )
    };


    Object.values(steps).forEach(
        (step) => {

            if (step) {
                step.classList.remove(
                    "active"
                );
            }

        }
    );


    if (
        activeStep &&
        steps[activeStep]
    ) {

        steps[activeStep].classList.add(
            "active"
        );

    }

}


function updateModelProgress(
    status
) {

    const progressBar =
        document.getElementById(
            "modelProgressBar"
        );


    const progressLabel =
        document.getElementById(
            "modelProgressLabel"
        );


    if (!progressBar) {
        return;
    }


    let width = 0;
    let label = "Idle";
    let step = null;


    switch (status) {

        case "unloading":

            width = 25;
            label = "Unloading";
            step = "unload";

            break;


        case "loading":

            width = 50;
            label = "Loading";
            step = "load";

            break;


        case "generating":

            width = 100;
            label = "Generating";
            step = "generate";

            break;


        case "loaded":

            width = 100;
            label = "Ready";
            step = "ready";

            break;


        case "error":

            width = 0;
            label = "Error";
            step = null;

            break;


        default:

            width = 0;
            label = "Idle";
            step = null;

    }


    progressBar.style.width =
        `${width}%`;


    if (progressLabel) {

        progressLabel.textContent =
            label;

    }


    setModelStep(step);

}


function formatModelSize(
    sizeGb
) {

    if (
        sizeGb === null ||
        sizeGb === undefined ||
        Number.isNaN(Number(sizeGb))
    ) {

        return "—";

    }


    return `${Number(sizeGb).toFixed(2)} GB`;

}


async function updateModelStatus() {

    try {

        const response =
            await fetch(
                MODEL_STATUS_URL,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                `Model status returned HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        const status =
            data.status || "idle";


        const requestedModel =
            data.requested_model;


        const activeModel =
            data.active_model ||
            data.ollama_loaded_model;


        const loadedModel =
            data.ollama_loaded_model;


        const runtimeStatus =
            document.getElementById(
                "modelRuntimeStatus"
            );


        const runtimeName =
            document.getElementById(
                "modelRuntimeName"
            );


        const runtimeMessage =
            document.getElementById(
                "modelRuntimeMessage"
            );


        const loadedName =
            document.getElementById(
                "modelLoadedName"
            );


        const loadedSize =
            document.getElementById(
                "modelLoadedSize"
            );


        const contextLength =
            document.getElementById(
                "modelContextLength"
            );


        const previousName =
            document.getElementById(
                "modelPreviousName"
            );


        if (runtimeStatus) {

            runtimeStatus.textContent =
                status === "error"
                    ? "Error"
                    : status === "idle"
                        ? "Idle"
                        : "Live";


            if (
                status === "error"
            ) {

                runtimeStatus.classList.remove(
                    "connected"
                );

            } else {

                runtimeStatus.classList.add(
                    "connected"
                );

            }

        }


        if (runtimeName) {

            runtimeName.textContent =
                requestedModel ||
                activeModel ||
                loadedModel ||
                "No model request";

        }


        if (runtimeMessage) {

            runtimeMessage.textContent =
                data.message ||
                "Waiting for model activity...";

        }


        if (loadedName) {

            loadedName.textContent =
                loadedModel ||
                "None";

        }


        if (loadedSize) {

            loadedSize.textContent =
                formatModelSize(
                    data.ollama_loaded_size_gb
                );

        }


        if (contextLength) {

            contextLength.textContent =
                data.ollama_context_length
                    ? `${data.ollama_context_length} tokens`
                    : "—";

        }


        if (previousName) {

            previousName.textContent =
                data.previous_model ||
                "None";

        }


        updateModelProgress(
            status
        );


    } catch (error) {

        console.error(
            "Could not update model status:",
            error
        );


        const runtimeStatus =
            document.getElementById(
                "modelRuntimeStatus"
            );


        const runtimeMessage =
            document.getElementById(
                "modelRuntimeMessage"
            );


        if (runtimeStatus) {

            runtimeStatus.textContent =
                "Offline";


            runtimeStatus.classList.remove(
                "connected"
            );

        }


        if (runtimeMessage) {

            runtimeMessage.textContent =
                "Model runtime status is currently unavailable.";

        }

    }

}


/* =========================================================
   INITIALIZATION
   ========================================================= */

loadConversation();

questionInput.focus();


/*
   Start live system monitoring.

   The first update happens immediately,
   followed by automatic updates every second.
*/

updateSystemStats();

setInterval(
    updateSystemStats,
    1000
);


/*
   Start live model monitoring.

   The model status is checked every second.
*/

updateModelStatus();

setInterval(
    updateModelStatus,
    1000
);
