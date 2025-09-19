// ----------------------------- Adjust footer position ----------------------------
// At content of page loaded
document.addEventListener("DOMContentLoaded", () => {
    var footer = document.getElementById("footer");

    function updateFooter() {
        if (document.body.scrollHeight <= window.innerHeight) {
            footer.classList.add("footer_normal");
            footer.classList.remove("footer_exceed");
        } else {
            footer.classList.add("footer_exceed");
            footer.classList.remove("footer_normal");
        }
    }
    // Initial check
    updateFooter();
    // Update on resize
    window.addEventListener("resize", updateFooter);
});

// ---------------------------- Change Color of buttons according to application link --------------
const urlInput = document.getElementById("url");
var search = document.getElementById("search");
var cancel = document.getElementById("cancel");
var cover = document.getElementById("cover");
var btns = document.querySelectorAll(".download");

colors_vid(urlInput);
colors_vid_prog(urlInput);

urlInput.addEventListener("input", () => {
    colors_vid(urlInput)
    colors_vid_prog(urlInput)
});

// Change button colors and cover size
function colors_vid(urlInput) {
    var url = urlInput.value.toLowerCase(); // get current value
    if (url.includes("facebook.com")) {
        search.style.background = "#3b5998";
        cancel.style.background = "#3b5998";
        btns.forEach(btn => {
            btn.style.background = "#3b5998";
        });
        cover.style.width="500px";
        cover.style.width="700px";
    }
    else if (url.includes("tiktok.com")) {
        search.style.background = "#1a1a1a";
        cancel.style.background = "#1a1a1a";
        btns.forEach(btn => {
            btn.style.background = "#1a1a1a";
        });
        cover.style.width="500px";
        cover.style.width="700px";
    }
    else if (url.includes("instagram.com")) {
        search.style.background = "#E1306C";
        cancel.style.background = "#E1306C";
        btns.forEach(btn => {
            btn.style.background = "#E1306C";
        });
        cover.style.width="500px";
        cover.style.width="700px";
    }
    else {
        search.style.background = "#FF0000";
        cancel.style.background = "#FF0000";
        btns.forEach(btn => {
            btn.style.background = "#FF0000";
        });
        cover.style.width="500px";
        cover.style.width="300px";
    }
}

// Change color of progress bar
function colors_vid_prog(urlInput) {
    let styleSheet = document.styleSheets[0];
    var url = urlInput.value.toLowerCase(); // get current value
    for (let i = 0; i < styleSheet.cssRules.length; i++) {
        let rule = styleSheet.cssRules[i];

        if (rule.selectorText === "progress::-webkit-progress-value") {
            if (url.includes("facebook.com")) {
                rule.style.backgroundColor = "#3b5998";
            }
            else if (url.includes("tiktok.com")) {
                rule.style.backgroundColor = "#1a1a1a";

            }
            else if (url.includes("instagram.com")) {
                rule.style.backgroundColor = "#E1306C";
            }
            else {
                rule.style.backgroundColor = "#FF0000";
            }
        }

        if (rule.selectorText === "progress::-moz-progress-bar") {
            if (url.includes("facebook.com")) {
                rule.style.backgroundColor = "#3b5998";
            }
            else if (url.includes("tiktok.com")) {
                rule.style.backgroundColor = "#1a1a1a";

            }
            else if (url.includes("instagram.com")) {
                rule.style.backgroundColor = "#E1306C";
            }
            else {
                rule.style.backgroundColor = "#FF0000";
            }
        }
    }
}

//----------------------------- At download start prevent any another downloads -------------------
var form_download = document.getElementById("video_downloader")
var submitted = false
form_download.addEventListener("submit", (event) => {
    let btn = event.submitter; // clicked button
    if (btn && btn.id === "search") {
        // هنا اعمل سيرش عادي وامنع تشغيل البروجرس
        submitted = false;
        return; // خروج من الفنكشن
    }

    // Submitted is true --> prevent any action (search or download) but cancel work
    if (submitted) {
        event.preventDefault();
        return false;
    }

    document.getElementById("progress-cancel").style.display = "flex";
    console.log(document.getElementById("progress-cancel").style.width)
    submitted = true;
    // Update progress bar by current downloading values
    updateProgress();
});

//------------------- Cancel downloading ------------------------------

// at cancel clicked will cancel download
var cancel = document.getElementById("cancel")
cancel.addEventListener("click", (event) => {
    event.preventDefault(); // Do not create another page
    submitted = false; // to make another submit 
    var url = cancel.dataset.url;
    fetch(url, { method: "POST" }) // Send request to server (POST) to "/cancel" in flask

    document.getElementById("progress-cancel").style.display = "none";
})


//--------------------------- Representing values of download progress --------------------
let progressBar = document.getElementById("download_prog");
let progressText = document.getElementById("progress-text");

function updateProgress() {
    fetch("/progress")
        .then(res => res.json())
        .then(data => {
            let percent = data.progress;
            progressBar.value = parseInt(percent);
            progressText.textContent = parseInt(percent) + "%";
            if (percent < 100) {
                setTimeout(updateProgress, 1000);
            }
        });
}