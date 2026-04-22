import { api } from "./api.js"

// delete dialog
const deleteButtons = document.querySelectorAll('#delete-button') // кнопки открытия диалога удаления
const deleteDialog = document.querySelector('#delete-dialog') // диалог удаления
const closeDeleteDialog = document.querySelector('#delete-close') // кнопка закрытия диалога
// edit dialog
const editButtons = document.querySelectorAll('#edit-button') // кнопки открытия диалога редактирования
const editDialog = document.querySelector('#edit-dialog') // диалог редактирования
const closeEditDialog = document.querySelector('#edit-close') // кнопка закрытия диалога редактирования

async function getOuterData(id) {
  editDialog.querySelector('#editId').value = id
  // Обновляем action формы с правильным id
  const form = editDialog.querySelector('#edit-form')
  form.action = `${api.bme280_outer}/${id}/update`
  
  try {
    const response = await fetch(`${api.bme280_outer}/${id}/data`)
    const data = await response.json()
    editDialog.querySelector('#created-at').textContent = new Date(data.created_at).toLocaleString('ru')
    editDialog.querySelector('#temperature').value = data?.temperature || ''
    editDialog.querySelector('#humidity').value = data?.humidity || ''
    editDialog.querySelector('#pressure').value = data?.pressure || ''
  } catch (error) {
    console.error('Error fetching outer data:', error)
    alert('Ошибка при загрузке данных записи')
  }
}

function init() {
  if (editButtons.length && editDialog) {
    editButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        getOuterData(id)
        editDialog.showModal()
      })
    })
  }

  if (closeEditDialog && editDialog) {
    closeEditDialog.addEventListener('click', () => {
      editDialog.close()
    })
  }

  if (closeDeleteDialog && deleteDialog) {
    closeDeleteDialog.addEventListener('click', () => {
      deleteDialog.close()
    })
  }

  if (deleteButtons.length && deleteDialog) {
    deleteButtons.forEach((button) => {
      button.addEventListener('click', async (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        const form = deleteDialog.querySelector(`#delete-form`)
        if (form) {
          form.action = `${api.bme280_outer}/${id}/delete`
        }
        // Загружаем дату записи для отображения
        try {
          const response = await fetch(`${api.bme280_outer}/${id}/data`)
          const data = await response.json()
          deleteDialog.querySelector('#delete-date').textContent = data.created_at
        } catch (error) {
          console.error('Error fetching outer data:', error)
        }
        deleteDialog.showModal()
      })
    })
  }
}

init()
