// Bot pop-up intro
document.addEventListener("DOMContentLoaded", () => {
    const elemsTap = document.querySelector(".tap-target");
    // eslint-disable-next-line no-undef
    const instancesTap = M.TapTarget.init(elemsTap, {});
    instancesTap.open();
    setTimeout(() => {
        instancesTap.close();
    }, 4000);
});

/* import components */
// include('./static/js/components/index_text.js');

window.addEventListener('load', () => {
    // initialization
    $(document).ready(() => {
        // Bot pop-up intro
        $("div").removeClass("tap-target-origin");

        // drop down menu for close, restart conversation & clear the chats.
        $(".dropdown-trigger").dropdown();

        // initiate the modal for displaying the charts,
        // if you dont have charts, then you comment the below line
        $(".modal").modal();

        // enable this if u have configured the bot to start the conversation.
        // showBotTyping();
        // $("#userInput").prop('disabled', true);

        // if you want the bot to start the conversation
        // customActionTrigger();
    });
    // Toggle the chatbot screen
    $("#profile_div").click(() => {
        $(".profile_div").toggle();
        // send("hi");
        $(".widget").toggle();
    });

    // clear function to clear the chat contents of the widget.
    $("#clear").click(() => {
        $(".chats").fadeOut("normal", () => {
            $(".chats").html("");
            $(".chats").fadeIn();
        });
    });

    // close function to close the widget.
    $("#close").click(() => {
        $(".profile_div").toggle();
        $(".widget").toggle();
        // scrollToBottomOfResults();
    });
});