$(document).ready(function () {
    x = 1;
    while (x <= number_strategies) {
        var act = +String(x)

        // Get the modal
        var modal = document.getElementById("myModal"+act);

        // Get the image and insert it inside the modal - use its "alt" text as a caption
        var img = document.getElementById("myImg"+act);
        var modalImg = document.getElementById("img"+act);
        var captionText = document.getElementById("caption"+act);
        img.onclick = function () {
            modal.style.display = "block";
            modalImg.src = this.src;
            captionText.innerHTML = this.alt;
        }

        // Get the <span> element that closes the modal
        var span = document.getElementById("close" + act);

        // When the user clicks on <span> (x), close the modal
        span.onclick = function () {
            modal.style.display = "none";
        }
        x++;
    }
})
