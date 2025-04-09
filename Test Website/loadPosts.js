let posts = [];
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("blog-posts");
    const loadMoreBtn = document.getElementById("load-more");

    // Load meta.json once
    fetch("./posts/meta.json")
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                console.error("meta.json is not a valid list.");
                return;
            }

            posts = data;
            loadNextPost(); // Load the first post on page load

            loadMoreBtn.addEventListener("click", loadNextPost);
        })
        .catch(err => console.error("Error loading posts:", err));

    function loadNextPost() {
        const postsToLoad = Math.min(6, posts.length - currentIndex); // Load 6 or remaining posts
        if (postsToLoad <= 0) {
            loadMoreBtn.style.display = "none"; // Hide button if no more posts
            return;
        }

        for (let i = 0; i < postsToLoad; i++) {
            const post = posts[currentIndex];
            currentIndex++;

            const article = document.createElement("article");
            article.className = "blog-post";

            const link = document.createElement("a");
            link.className = "blog-post-link";
            link.href = `./posts/${post.filename}`;

            const contentDiv = document.createElement("div");
            contentDiv.className = "blog-post-content";

            const img = document.createElement("img");
            img.src = post.cover_image || "";
            img.alt = post.title || "Missing Image";

            const title = document.createElement("h2");
            title.textContent = post.title || "Untitled";

            const date = document.createElement("p");
            date.textContent = post.date || "";

            contentDiv.appendChild(img);
            contentDiv.appendChild(title);
            contentDiv.appendChild(date);
            link.appendChild(contentDiv);
            article.appendChild(link);
            container.appendChild(article);
        }
    }
});
