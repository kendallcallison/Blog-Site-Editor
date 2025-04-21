let posts = [];
let currentIndex = 0;
let sortOrder = "desc"; // Default to newest first

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("blog-posts");
    const loadMoreBtn = document.getElementById("load-more");
    const searchBar = document.getElementById("search-bar");
    const sortDropdown = document.getElementById("sort-order");

    fetch("./posts/meta.json")
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                console.error("meta.json is not a valid list.");
                return;
            }

            posts = data;
            applySorting(); // Apply initial sort
            loadNextPost();

            loadMoreBtn.addEventListener("click", loadNextPost);
            searchBar.addEventListener("input", handleSearch);
            sortDropdown.addEventListener("change", () => {
                sortOrder = sortDropdown.value;
                posts = applySorting(posts);
                currentIndex = 0;
                clearPosts();
                handleSearch(); // refresh with new sorted order
            });
        })
        .catch(err => console.error("Error loading posts:", err));

    function clearPosts() {
        container.innerHTML = "";
    }

    function createPostElement(post) {
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
        return article;
    }

    function loadNextPost() {
        const postsToLoad = Math.min(9, posts.length - currentIndex);
        if (postsToLoad <= 0) {
            loadMoreBtn.style.display = "none";
            return;
        }

        for (let i = 0; i < postsToLoad; i++) {
            const post = posts[currentIndex++];
            const article = createPostElement(post);
            container.appendChild(article);
        }
    }

    function handleSearch() {
        const query = searchBar.value.toLowerCase();
        clearPosts();

        let filtered = [...posts];
        if (query.trim() !== "") {
            filtered = filtered.filter(post =>
                post.title.toLowerCase().includes(query) ||
                post.date.toLowerCase().includes(query)
            );
            loadMoreBtn.style.display = "none";
        } else {
            currentIndex = 0;
            loadMoreBtn.style.display = "block";
        }

        filtered = applySorting(filtered);

        if (filtered.length === 0) {
            container.innerHTML = "<p>No posts found.</p>";
            loadMoreBtn.style.display = "none";
        } else if (query.trim() === "") {
            loadNextPost(); // Reload posts from the top
        } else {
            filtered.forEach(post => {
                const article = createPostElement(post);
                container.appendChild(article);
            });
        }
    }

    function applySorting(list = posts) {
        const sorted = [...list];
        sorted.sort((a, b) => {
            const nameA = a.filename;
            const nameB = b.filename;
            return sortOrder === "asc"
                ? nameA.localeCompare(nameB)
                : nameB.localeCompare(nameA);
        });
        if (list === posts) posts = sorted;
        return sorted;
    }
});
