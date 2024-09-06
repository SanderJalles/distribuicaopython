function handleUpload(event) {
    event.preventDefault();  // Prevenir o comportamento padrão do formulário

    const formData = new FormData(event.target);  // Pegando os dados do formulário

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            return response.json();
        } else {
            return response.blob();
        }
    })
    .then(data => {
        if (data instanceof Blob) {
            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'processosdistribuidos_completos.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            if (data.status === "warning") {
                let message = data.message;
                if (data.duplicados && data.duplicados.length > 0) {
                    message += "\n\n" + data.duplicados.join("\n");
                }
                showPopup(message);
            } else if (data.status === "success") {
                alert("Processos distribuídos com sucesso!");
            } else if (data.status === "error") {
                alert("Erro: " + data.message);
            }
        }
    })
    .catch(error => {
        alert("Erro ao fazer upload: " + error);
    });
}

function showPopup(message) {
    const popup = document.getElementById("popup");
    popup.querySelector("span").innerText = message;
    popup.style.display = "block";
}

function closePopup() {
    const popup = document.getElementById("popup");
    popup.style.display = "none";
}

// Adicionar o event listener para o formulário
document.getElementById('uploadForm').addEventListener('submit', handleUpload);
