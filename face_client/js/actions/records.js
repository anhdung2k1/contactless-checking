function renderRecordTable(records) {
    const tbody = document.querySelector('#recordTable tbody');
    tbody.innerHTML = '';

    records.forEach((record) => {
        const row = document.createElement('tr');

        // Set badge class based on record.status
        const badgeClass = record.status === 'success' ? 'badge bg-success' : 'badge bg-danger';

        row.innerHTML = `
            <td class="d-none d-md-table-cell">${record.recordData}</td>
            <td><span class="${badgeClass}">${record.status}</span></td>
            <td class="d-none d-xl-table-cell">${record.createAt}</td>
        `;

        tbody.append(row);
    });
}

const getAllRecords = async (dateStr) => {
    try {
        const response = await fetch(`${HOST_IP}/api/records/query?date=${encodeURIComponent(dateStr)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch all records');
        }

        const recordData = await response.json();
        renderRecordTable(recordData);
    } catch (error) {
        console.error('Get Records failed: ', error);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    getAllRecords(getCurrentDate()); // Fetch all records for the current date when the page loads
});

function getCurrentDate() {
    const date = new Date();
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateString(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

document.addEventListener("DOMContentLoaded", function() {
    const datePicker = document.getElementById("datetimepicker-dashboard").flatpickr({
        inline: true,
        prevArrow: "<span title='Previous month'>&laquo;</span>",
        nextArrow: "<span title='Next month'>&raquo;</span>",
        defaultDate: getCurrentDate(),
        onChange: function(selectedDates) {
            if (selectedDates.length > 0) {
                const formattedDate = formatDateString(selectedDates[0]);
                console.log("Selected date: ", formattedDate);
                getAllRecords(formattedDate); // Fetch records for the selected date
            }
        }
    });
    console.log("Flatpickr instance: ", datePicker);
});
