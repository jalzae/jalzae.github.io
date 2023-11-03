const name = document.getElementById('name')

const message = document.getElementById('message')
const list_pesan = document.getElementById('list_pesan')
const forms =document.getElementById('forms')

forms.onsubmit=(e)=> {
  e.preventDefault();
  
  if(name.value==''){
    alert('Nama kamu kosong')
    return
  }
  
  if(message.value==''){
    alert('Pesan kamu kosong')
    return
  }
  
  if(name.value && message.value){
    list_pesan.innerHTML+=`<li>${name.value}: ${message.value}</li>`
    
    name.value=''
    message.value=''
  }
  
}

// kita dapat element nama,pesan
// kita buat ketika tekan enter/kirim itu akan mengirim pesan ke list_pesan 

