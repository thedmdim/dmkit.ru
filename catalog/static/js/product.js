document.addEventListener('DOMContentLoaded', showPrice, false);
document.querySelectorAll("input[cost]").forEach(element => element.onclick = showPrice)
document.querySelectorAll("#thumbnails>img").forEach(element => element.onclick = showImg)

function collapse(){
	document.querySelectorAll(".collapsible").forEach(element => element.style.display === "grid" ? element.style.display = "none" : element.style.display = "grid");	
}

function view(){
	document.querySelector("button[type=submit]").scrollIntoView({behavior: "smooth"});
}

let getAll = () => {
	document.querySelectorAll("p[cost]")
}

function showPrice(){
	document.querySelector("#price").innerHTML = [...document.querySelectorAll("input[cost]")].reduce((a,c)=>a+(c.checked ? parseInt(c.getAttribute("cost")) : 0), 0)+" RUB"
}

function showImg(){
	document.querySelector("#gallery>img").src = this.src;
}