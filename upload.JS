document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');

    uploadForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(uploadForm);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "warning") {
                alert(data.message);
            } else if (data.status === "success") {
                alert("Processos distribuídos com sucesso!");
            } else if (data.status === "error") {
                alert("Erro: " + data.message);
            }
        })
        .catch(error => {
            alert("Erro ao fazer upload: " + error);
        });
    });
});
