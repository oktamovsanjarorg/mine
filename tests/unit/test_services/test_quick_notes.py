import pytest
from src.services.quick_note import QuickNoteService

@pytest.fixture
def quick_note_service(async_session):
    return QuickNoteService(async_session)

@pytest.mark.asyncio
async def test_quick_notes_lifecycle(quick_note_service, test_user):
    note = await quick_note_service.create(test_user.id, "Test tezkor eslatma", is_pinned=False)
    assert note.id is not None
    assert note.content == "Test tezkor eslatma"
    assert note.is_pinned is False

    pinned = await quick_note_service.toggle_pin(note.id)
    assert pinned is True

    pinned_list = await quick_note_service.get_pinned(test_user.id)
    assert len(pinned_list) >= 1
    assert pinned_list[0].id == note.id

    search_res = await quick_note_service.search(test_user.id, "tezkor")
    assert len(search_res) >= 1
    assert search_res[0].id == note.id

    deleted = await quick_note_service.delete(note.id)
    assert deleted is True
