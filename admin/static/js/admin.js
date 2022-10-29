function add_item(){
    let inputs = document.querySelector("#items").querySelectorAll("p")
    let last = inputs[inputs.length - 1]

    let lastNum = parseInt(last.querySelector("input").name.replace("item",""))+1

    let p = document.createElement('p');
    p.innerHTML = `<input type="text" name="item${lastNum}" placeholder="Item name"><input type="number" name="cost${lastNum}" placeholder="Cost">`;
    last.after(p)
}

