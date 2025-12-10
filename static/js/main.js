
const likeForm = document.querySelector(".like-form");

if(likeForm){
    const likeBtn = likeForm.querySelector(".js-like-btn");
    const likesCount = document.querySelector(".likes-count");

    likeForm.addEventListener("submit", function (event) {
        event.preventDefault();

        fetch(likeForm.action, {
            method: "POST",
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (!data.success && data.error === "not_logged_in") {
                    window.location.href = "/login";
                    return;
                }

                if (data.userliked) {
                    likeBtn.classList.remove("like-btn");
                    likeBtn.classList.add("liked-btn");
                } else {
                    likeBtn.classList.remove("liked-btn");
                    likeBtn.classList.add("like-btn");
                }
                likesCount.textContent = data.likes_count;
            })
    });    
}

