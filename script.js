function handleUpload(event) {
    event.preventDefault();  // Previne o comportamento padrão do formulário

    const formData = new FormData(event.target);  // Captura os dados do formulário

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        // Verificar o tipo de conteúdo da resposta
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            return response.json();  // Se for JSON, processa como JSON
        } else if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
            return response.blob();  // Se for um arquivo Excel, processa como Blob
        } else {
            throw new Error("Tipo de resposta desconhecido: " + contentType);
        }
    })
    .then(data => {
        if (data instanceof Blob) {
            // Se a resposta for um arquivo Excel, processa o download
            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'processosdistribuidos_completos.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else if (data.status === "warning") {
            alert(data.message);  // Alerta de aviso
        } else if (data.status === "success") {
            alert("Processos distribuídos com sucesso!");  // Alerta de sucesso
        } else if (data.status === "error") {
            alert("Erro: " + data.message);  // Alerta de erro
        }
    })
    .catch(error => {
        alert("Erro ao fazer upload: " + error);
    });
}

document.getElementById('uploadForm').addEventListener('submit', handleUpload);
