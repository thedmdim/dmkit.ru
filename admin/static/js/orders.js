document.querySelector("#payment").checked = (getCookie(document.cookie)["payment"] === "true")
let curUrl = window.location.search
let curParams = new URLSearchParams(curUrl)
document.querySelector("#back").onclick = () => {location.search = (curParams.get("page") && curParams.get("page")>0) ? "page="+(curParams.get("page")-1) : "page=0"; return false;}
document.querySelector("#forward").onclick = () => {location.search = curParams.get("page") ? "page="+(parseInt(curParams.get("page"))+1) : "page=1"; return false;}


function getCookie(cookie){
    let cks = {};
    cookie.split(";").forEach(value => {let lst = value.split("="); cks[lst[0]]=lst[1]})
    return cks
}

function setPaid(){
    let status = document.querySelector("#payment").checked
    document.cookie=`payment=${status}`
}
