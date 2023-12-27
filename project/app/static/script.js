const deleteForms = document.getElementsByClassName('item-delete-form');
const changeInputs = document.getElementsByClassName('item-change-input');
const addButtons = document.getElementsByClassName('add-button');
const subButtons = document.getElementsByClassName('sub-button');
const addForms = document.getElementsByClassName('add-form');
const changeInterval = 750;

const onChangeSubmit = (form) => {
    const formData = new FormData(form);
    const payload = new URLSearchParams(formData);
        
    fetch('/cart/change/', {
    method: 'POST',
    body: payload,
    })
    .then(res => res.json())
    .then(data => console.log(data["message"]))
}

const onInputChange = (input) => {
    clearTimeout(input.timerId);    
    input.timerId = setTimeout(()=>{
    onChangeSubmit(input.parentNode);   
    }, changeInterval);  
}


[...addForms].forEach(form => {
 form.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(form);
    const payload = new URLSearchParams(formData);
    
    fetch('/cart/add/', {
    method: 'POST',
    body: payload,
    })
    .then(res => res.json())
    .then(data => alert(data["message"]))
    })
});


[...deleteForms].forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const payload = new URLSearchParams(formData);
        
        fetch('/cart/delete/', {
        method: 'POST',
        body: payload,
        })
        .then(res => res.json())
        .then(() => {
            div = form.parentNode.parentNode;
            div.parentNode.removeChild(div);
        })
    }) 
});

[...changeInputs].forEach(input => {
    input.addEventListener('change', function(e) {
        onInputChange(input);     
    })
});

[...addButtons].forEach(button => {
    button.addEventListener('click', function(e) {
        input = button.parentNode.querySelector('input[name="count"]'); 
        input.value = Number(input.value) + 1; 
        if(input.classList.contains('item-change-input'))
            onInputChange(input);  
    })
});
[...subButtons].forEach(button => {
    button.addEventListener('click', function(e) {
        input = button.parentNode.querySelector('input[name="count"]'); 
        input.value = Number(input.value) - 1; 
        if(input.classList.contains('item-change-input'))  
            onInputChange(input);  
    })
});
