window.onload=function(){

    const pw_show_hide = document.querySelector('.pw_show_hide')
    const input_id = this.document.querySelector('input[type=text]')
    const input_pw = this.document.querySelector('input[type=password]')
    const id_error = this.document.querySelector('.id_error')
    const pw_error = this.document.querySelector('.pw_error')
    console.log(pw_show_hide)

    input_id.addEventListener("click", () => {
        id_error.style.display = 'block'
    })
    input_pw.addEventListener("click", () => {
        pw_error.style.display = 'block'
    })
    

    let b = true
    pw_show_hide.addEventListener('click',() => {
        if(b==true){
            pw_show_hide.style.backgroundPosition = '-125px 0';
            b=false;
        } else {
            pw_show_hide.style.backgroundPosition = '-105px 0';
            b=true;
        }
    });
}//onload end
