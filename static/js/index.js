document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const searchForm = document.getElementById("searchForm");

  if (searchInput && searchForm) {
    searchInput.addEventListener("input", function () {
      clearTimeout(this.delay);
      this.delay = setTimeout(() => {
        searchForm.submit();
      }, 500);
    });
  }
});
