function showConfirmationModal(commentId) {
    Swal.fire({
        title: 'Вы точно хотите удалить комментарий?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#000000',
        confirmButtonText: 'Да!',
        cancelButtonText: 'Нет'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('delete-form-' + commentId).submit();
        }
    });
}
