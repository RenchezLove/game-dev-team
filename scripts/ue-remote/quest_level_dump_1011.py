import unreal
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
world = unreal.UnrealEditorSubsystem().get_editor_world()
keys = ['Barrier', 'Guard', 'Scientist', 'Elder', 'Trader', 'QuestItemSpawner', 'EnemyBase', 'Bandit', 'WolfDen', 'Campfire', 'VillageZone', 'TargetPoint', 'PlayerStart', 'StashChest']
out = []
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    cls = a.get_class().get_name(); tags = [str(t) for t in a.tags]
    if any(k in cls for k in keys) or any(t.startswith('DebugTP_') for t in tags):
        l = a.get_actor_location(); r = a.get_actor_rotation()
        extra = ''
        for p in ['open_when_taken_quest_id', 'open_when_turned_in_quest_id', 'npc_tag', 'item_row', 'quest_id', 'talk_radius', 'interact_radius']:
            try: extra += ' %s=%s' % (p, a.get_editor_property(p))
            except Exception: pass
        out.append('QDUMP|%s|%s|%d|%d|%d|yaw=%d|%s|%s' % (cls, a.get_actor_label(), l.x, l.y, l.z, r.yaw, ','.join(tags), extra))
for s in sorted(out): print(s)
import re
def qfields(q):
    t = q.export_text()
    return ' '.join(re.findall(r'(?:QuestId|MapMarkerTag|TurnInNpcTag|KillTargetTag|TargetCount|RequiredItemName|RequiredItemCount|GiverNpcTag|Kind)=[^,()]*', t)) + ' GiveOnAccept=' + ''.join(re.findall(r'GiveOnAccept=\(.*?\)\)', t)) + ' RewardItems=' + ''.join(re.findall(r'RewardItems=\(.*?\)\)', t))
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    cls = a.get_class().get_name()
    for p in ['quest_marker_tag', 'first_quest_row', 'second_quest_row', 'third_quest_row', 'notebook_wait_seconds', 'enemy_tag', 'base_display_name']:
        try: print('QPROP|%s|%s|%s=%s' % (cls, a.get_actor_label(), p, a.get_editor_property(p)))
        except Exception: pass
    for p in ['offered_quest', 'second_quest', 'third_quest']:
        try: print('QQUEST|%s|%s|%s| %s' % (cls, a.get_actor_label(), p, qfields(a.get_editor_property(p))))
        except Exception: pass
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_class().get_name() == 'QuestItemSpawner':
        for p in ['only_while_quest_taken', 'check_interval', 'pickup_class']:
            try: print('QSPOT|%s|%s=%s' % (a.get_actor_label(), p, a.get_editor_property(p)))
            except Exception as e: print('QSPOT|err', p, e)
        l = a.get_actor_location()
        for b in unreal.EditorLevelLibrary.get_all_level_actors():
            bl = b.get_actor_location()
            if b != a and abs(bl.x - l.x) < 400 and abs(bl.y - l.y) < 400: print('QSPOT|near|%s|%s|%d|%d' % (b.get_class().get_name(), b.get_actor_label(), bl.x, bl.y))
