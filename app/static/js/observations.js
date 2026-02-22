// create dialog
const createDialog = document.querySelector('#create-dialog') // диалог создания
const createButton = document.querySelector('#create-button') // кнопка открытия диалога
const closeCreateDialog = document.querySelector('#create-close') // кнопка закрытия диалога
// delete dialog
const deleteButtons = document.querySelectorAll('#delete-button') // кнопки открытия диалога удаления
const deleteDialog = document.querySelector('#delete-dialog') // диалог удаления
const closeDeleteDialog = document.querySelector('#delete-close') // кнопка закрытия диалога
// edit dialog
const editButtons = document.querySelectorAll('#edit-button') // кнопки открытия диалога редактирования
const editDialog = document.querySelector('#edit-dialog') // диалог редактирования
const closeEditDialog = document.querySelector('#edit-close') // кнопка закрытия диалога редактирования

async function getObservationData(id) {
  editDialog.querySelector('#editId').value = id
  try {
    const response = await fetch(`/api/observations/${id}/data`)
    const data = await response.json()
    editDialog.querySelector('#created-at').textContent = data.created_at
    editDialog.querySelector('#cloudiness').value = data.cloudiness || 'clear'
    editDialog.querySelector('#precipitation').value = data.precipitation || 'none'
    editDialog.querySelector('#precipitation-rate').value = data.precipitation_rate || 'none'
    editDialog.querySelector('#snow-depth').value = data.snow_depth || 0
  } catch (error) {
    console.error('Error fetching observation data:', error)
    alert('Ошибка при загрузке данных записи')
  }
}

function init() {
  if (createDialog && createButton) {
    createButton.addEventListener('click', () => {
      createDialog.showModal()
    })
  }

    if (createDialog &&closeCreateDialog) {
    closeCreateDialog.addEventListener('click', () => {
      createDialog.close()
    })
  }

  if (editButtons.length && editDialog) {
    editButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        getObservationData(id)
        editDialog.showModal()
      })
    })
  }

  if (closeEditDialog && editDialog) {
    closeEditDialog.addEventListener('click', () => {
      editDialog.hidePopover()
    })
  }


  if (closeDeleteDialog && deleteDialog) {
    closeDeleteDialog.addEventListener('click', () => {
      deleteDialog.close()
    })
  }

  if (deleteButtons.length && deleteDialog) {
    deleteButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        const form = deleteDialog.querySelector(`#delete-form`)
        if (form) {
          form.action = `/api/observations/${id}/delete`
        }
         deleteDialog.showModal()
      })
    })
  }
}

init()