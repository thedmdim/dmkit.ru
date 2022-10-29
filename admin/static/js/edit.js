// Represents edit form of whole product
class Product {
    get id () {return document.querySelector("#info > *[name=id]").value}
    set id (value) {document.querySelector("#info > *[name=id]").value = value}

    get slug () {return document.querySelector("#info > *[name=slug]").value}
    set slug (value) {document.querySelector("#info > *[name=slug]").value = value}

    get name () {return document.querySelector("#info > *[name=name]").value}
    set name (value) {document.querySelector("#info > *[name=name]").value = value}

    get desc () {return document.querySelector("#info > *[name=desc]").value}
    set desc (value) {document.querySelector("#info > *[name=desc]").value = value}

    get thumbnail () {
        const [file] = document.querySelector("input[name='thumbnail']").files;
        return file
    }
    set thumbnailExistingPreview (value) {document.querySelector("#thumbnail").src = `/catalog/static/pics/${value}`}
    set thumbnailNewPreview (value) {document.querySelector("#thumbnail").src = value}

    get manufacturer_id () {return document.querySelector("#info > *[name=manufacturer_id]").value}
    set manufacturer_id (value) {document.querySelector("#info > *[name=manufacturer_id]").value = value}

    get model_id () {return document.querySelector("#info > *[name=model_id]").value}
    set model_id (value) {document.querySelector("#info > *[name=model_id]").value = value}

    get items () {
        let items = Array.from(document.querySelectorAll("#items-container>.item"));
        let result = {
            unedited: [],
            edited: [],
            new: []
        }
        for (let i = 0; i < items.length; i++){
            let item = items[i]
            let itemObj = {
                id: item.id,
                name: item.querySelector("*[name=name]").value,
                price: item.querySelector("*[name=price]").value,
                type_id: item.querySelector("*[name=type]").value
            }
            if (item.id && !item.classList.contains("edited")){
                result.unedited.push(itemObj)
            }
            if (item.id && item.classList.contains("edited")){
                result.edited.push(itemObj)
            }
            if (!item.id){
                result.new.push(itemObj)
            }
        }
        return result
    }

    set items (items) {
        let itemsContainer = document.getElementById("items-container")
        itemsContainer.innerHTML = "";

        let itemNodes = items.map(item => new Item(item))
        itemNodes.forEach(element => itemsContainer.appendChild(element.itemNode))        
    }

    get gallery () {return document.querySelectorAll("#gallery>input[name=gallery]").files}

    set gallery (gallery) {
        let galleryContainer = document.getElementById("gallery-container")
        galleryContainer.innerHTML = "";

        let photos = gallery.map(filename => new Photo(`/catalog/static/pics/${filename}`))
        photos.forEach(element => {
            let deleteButton = document.createElement("button");
            deleteButton.setAttribute("type", "button");
            deleteButton.onclick = () => {
                console.log("hello form onclick");
                let src = element.photoNode.querySelector("img").src.split("/").pop();
                fetch(`/api/products/${product.id}/gallery/${src}`, {method: 'DELETE'});
                element.photoNode.remove()
            };
            deleteButton.innerHTML = "Удалить";
            element.photoNode.appendChild(deleteButton)
            galleryContainer.appendChild(element.photoNode);
            
        })
    }

    reflectProduct (product) {
        this.id = product.id
        this.slug = product.slug
        this.name = product.name
        this.desc = product.desc
        this.thumbnailExistingPreview = product.thumbnail
        this.manufacturer_id = product.manufacturer_id
        this.model_id = product.model_id

        this.items = product.items
        this.gallery = product.gallery
    }
}

class Item {
    itemNode = document.getElementById("master-item").firstElementChild.cloneNode(true);

    get id () {return this.itemNode.id}
    set id (value) {this.itemNode.id = value}

    get name () {return this.itemNode.querySelector("*[name=name]").value}
    set name (value) {this.itemNode.querySelector("*[name=name]").value = value}

    get price () {return this.itemNode.querySelector("*[name=price]").value}
    set price (value) {this.itemNode.querySelector("*[name=price]").value = value}

    get typeId () {return this.itemNode.querySelector("*[name=type]").value}
    set typeId (value) {this.itemNode.querySelector("*[name=type]").value = value}

    constructor(item){        
        this.id = item.id;
        this.name = item.name
        this.price = item.price
        this.typeId = item.type_id

        this.itemNode.addEventListener("change", (event) => {this.itemNode.classList.add("edited")})
    }
}

class Photo {
    photoNode = document.getElementById("master-photo").firstElementChild.cloneNode(true);

    get filename () {return this.photoNode.querySelector("img").src}
    set filename (value) {this.photoNode.querySelector("img").src = value}

    constructor(filename){
        this.filename = filename
    }
}

document.querySelectorAll('#create-or-edit select').onchange = loadProduct;
document.querySelector("#info>input[name=thumbnail]").onchange

var product = new Product()

async function loadProduct(option) {
    let productData = {
        id: "",
        slug: "",
        name: "",
        desc: "",
        thumbnail: "placeholder.png",
        manufacturer_id: "",
        model_id: "",

        items: new Array,
        gallery: new Array
    }
    console.log(productData)

    if (option.value) {
        productData = await fetch(`edit/api/products/${option.value}`).then(response => response.json());
    }
    product.reflectProduct(productData);
}

function addEmptyItem(){
    let item = document.getElementById("master-item").firstElementChild.cloneNode(true);
    let itemsContainer = document.getElementById("items-container")

    itemsContainer.appendChild(item)
}

async function deleteItem (button) {
    sure = confirm("Удалить деталь?")
    if (sure) {
        let item = button.parentElement;

        if (item.id) {
            fetch(`edit/api/products/${product.id}/items/${item.id}`, {method: 'DELETE'});
        }

        item.remove()
    }
}

function previewPhotos(input){
    let galleryContainer = document.getElementById("gallery-container");
    galleryContainer.querySelectorAll(".preview").forEach(element => element.remove());

    Array.from(input.files).forEach(element => {
        let photo = new Photo(URL.createObjectURL(element));
        photo.photoNode.classList.add("preview");
        galleryContainer.appendChild(photo.photoNode)
    })
}

// image-cropper
let productImg = document.getElementById("img")
let box = document.getElementById("cropper-box");
let cropper
document.onkeydown = function(evt) {
    if (box.style.display == "grid") {
        evt = evt || window.event;
        let isEscape = false;

        if ("key" in evt) {
            isEscape = (evt.key === "Escape" || evt.key === "Esc");
        } else {
            isEscape = (evt.keyCode === 27);
        }

        if (isEscape) {
            box.style.display = "none";
            cropper.destroy()
        }
    }
};

function getBase64(file) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = error => reject(error);
	});
};

function crop(){
	box.style.display = "grid";
	let file = productImg.files[0];
	let image = document.getElementById('image');

	getBase64(file).then(data => {
		image.src = data;
		cropper = new Cropper(image, {
		aspectRatio: 1,
		viewMode: 3,
		preview: "#preview"
		})
	});

}

function getCropped(){
	canvas = cropper.getCroppedCanvas({
            width: 150,
            height: 150,
        });
	box.style.display = "none";
	canvas.toBlob(blob => {
        let file = new File([blob], `${product.slug}.jpg`, {type:"image/jpeg", lastModified:new Date().getTime()});
        let container = new DataTransfer();
        container.items.add(file);
        console.log(container)
        document.querySelector("input[name=thumbnail]").files = container.files;
        console.log(document.querySelector("input[name=thumbnail]").files)
        product.thumbnailNewPreview = URL.createObjectURL(blob);
        cropper.destroy()
    })
}

// sending result
async function sendProduct(){
    let infoForm = document.querySelector("#info");
    let galleryForm = document.querySelector('#gallery')
    let res
    if (product.id) {
        // existing product modified: PUT

        res = await fetch(`edit/api/products/${product.id}`, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json'
            },
            body: new FormData(infoForm)
          });

    } else {
        res = await fetch("edit/api/products/", {
            method: 'POST',
            headers: {
                'Accept': 'application/json'
            },
            body: new FormData(infoForm)
          });
    }
        
    let p = await res.json()

    if (product.items.new.length) {
        res = await fetch(`edit/api/products/${p.id}/items`, {
            method: 'POST',
            body: JSON.stringify(product.items.new)
        })
    }

    if (product.items.edited.length) {
        res = await fetch(`edit/api/products/${p.id}/items`, {
            method: 'PUT',
            body: JSON.stringify(product.items.edited)
        })
    }

    if (galleryForm.querySelector("input").value != '') {

        console.log("gallery update")
        res = await fetch(`edit/api/products/${p.id}/gallery`, {
            method: 'POST',
            body: new FormData(galleryForm)
        });

        console.log(res)
    }


    
}