"""Screenshots Page - Upload and manage screenshot evidence.

This page allows product owners to:
- Upload screenshots of implemented features
- Add annotations and notes to screenshots
- Link screenshots to specific user stories
- View all uploaded screenshots

Related: US-111
"""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser


def main():
    """Screenshots management page."""
    st.title("📸 Screenshots & Evidence")
    st.markdown("### Upload and manage screenshot evidence for user stories")

    # Initialize uploads directory
    uploads_dir = Path(__file__).parent.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)

    # Get roadmap priorities for linking
    try:
        roadmap_path = PROJECT_ROOT / "docs" / "roadmap" / "ROADMAP.md"
        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()
        priority_options = ["None"] + [f"{p.get('number', '?')} - {p.get('name', 'Unknown')}" for p in priorities]
    except Exception as e:
        st.error(f"Failed to load ROADMAP: {e}")
        priority_options = ["None"]

    # Upload section
    st.header("📤 Upload Screenshot")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a screenshot file",
            type=["png", "jpg", "jpeg", "gif"],
            help="Upload a screenshot showing feature implementation",
        )

    with col2:
        linked_priority = st.selectbox(
            "Link to User Story",
            priority_options,
            help="Associate this screenshot with a specific user story",
        )

    if uploaded_file is not None:
        # Display image preview
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_container_width=True)

        # Annotation form
        st.markdown("### Add Annotations")

        annotation_title = st.text_input("Screenshot Title", value=f"Screenshot - {uploaded_file.name}")
        annotation_notes = st.text_area(
            "Notes & Observations",
            height=150,
            help="Describe what this screenshot demonstrates",
        )

        tags = st.multiselect(
            "Tags",
            ["Implemented", "Bug", "UI Issue", "Performance", "UX", "Validation", "Demo"],
            help="Add tags to categorize this screenshot",
        )

        # Save button
        if st.button("💾 Save Screenshot", type="primary"):
            try:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                priority_slug = (
                    linked_priority.split(" - ")[0].replace(" ", "_") if linked_priority != "None" else "general"
                )
                filename = f"{priority_slug}_{timestamp}_{uploaded_file.name}"
                save_path = uploads_dir / filename

                # Save image file
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Save metadata
                metadata = {
                    "title": annotation_title,
                    "notes": annotation_notes,
                    "tags": tags,
                    "linked_priority": linked_priority,
                    "filename": filename,
                    "uploaded_at": datetime.now().isoformat(),
                }

                metadata_path = uploads_dir / f"{filename}.meta.txt"
                metadata_path.write_text(str(metadata))

                st.success(f"✅ Screenshot saved successfully: {filename}")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Failed to save screenshot: {e}")

    # Divider
    st.markdown("---")

    # View uploaded screenshots
    st.header("🖼️ Uploaded Screenshots")

    # Get all uploaded images
    image_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg"))
    image_files += list(uploads_dir.glob("*.jpeg")) + list(uploads_dir.glob("*.gif"))

    if not image_files:
        st.info("No screenshots uploaded yet. Upload your first screenshot above!")
        return

    # Filter controls
    col1, col2 = st.columns(2)

    with col1:
        filter_priority = st.selectbox(
            "Filter by User Story",
            ["All"] + priority_options[1:],
            key="filter_priority",
        )

    with col2:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Name"])

    # Sort images
    if sort_by == "Newest First":
        image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    elif sort_by == "Oldest First":
        image_files.sort(key=lambda x: x.stat().st_mtime)
    else:
        image_files.sort(key=lambda x: x.name)

    # Display images in grid
    cols_per_row = 3
    for i in range(0, len(image_files), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(image_files):
                img_path = image_files[i + j]

                with col:
                    # Load and display image
                    try:
                        image = Image.open(img_path)
                        st.image(image, use_container_width=True)

                        # Load metadata if exists
                        meta_path = uploads_dir / f"{img_path.name}.meta.txt"
                        if meta_path.exists():
                            meta_content = meta_path.read_text()
                            st.caption(f"**{img_path.name}**")

                            # Extract title from metadata
                            if "title" in meta_content:
                                try:
                                    import ast

                                    meta_dict = ast.literal_eval(meta_content)
                                    if meta_dict.get("notes"):
                                        st.caption(meta_dict["notes"][:100] + "...")
                                    if meta_dict.get("tags"):
                                        st.caption(f"Tags: {', '.join(meta_dict['tags'])}")
                                except:
                                    pass
                        else:
                            st.caption(f"**{img_path.name}**")

                        # Actions
                        if st.button("🗑️ Delete", key=f"delete_{img_path.name}"):
                            img_path.unlink()
                            if meta_path.exists():
                                meta_path.unlink()
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error loading {img_path.name}: {e}")

    # Footer
    st.markdown("---")
    st.markdown(f"**Total Screenshots**: {len(image_files)}")


if __name__ == "__main__":
    main()
