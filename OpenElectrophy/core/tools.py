# -*- coding: utf-8 -*-
"""
Some tools for manipulating objects.


"""

import numpy as np




def merge_blocks(block_list, session = None, dbinfo = None):
    if session is None:
        from sqlmapper import globalsession
        session = globalsession
    assert session is not None, 'You must give a session'

    if dbinfo is None:
        from sqlmapper import globaldbinfo
        dbinfo = globaldbinfo
    assert dbinfo is not None, 'You must give a dbinfo'
    
    Block = dbinfo.get_class('Block')
    RecordingChannel = dbinfo.get_class('RecordingChannel')
    RecordingChannelGroup = dbinfo.get_class('RecordingChannelGroup')
    
    new_bl = Block(name = 'merged from {}'.format([bl.id for bl in block_list]))
    
    # merge RCG and RC
    old_rcs = { }
    old_rcgs = { }
    old_indexes = { }
    for bl in block_list:
        for rcg in bl.recordingchannelgroups:
            indexes = [ ]
            for rc  in rcg.recordingchannels:
                indexes.append(rc.index)
                if rc.index not in old_rcs:
                    old_rcs[rc.index] = [ ]
                old_rcs[rc.index].append(rc)
            if str(indexes) not in old_rcgs:
                old_rcgs[str(indexes)] = [ ]
            old_rcgs[str(indexes)].append(rcg)
            old_indexes[str(indexes)] = indexes
    new_rcs = {}
    for i in old_rcs:
        # we take the first name, coordinate, description
        rc0 = old_rcs[i][0]
        new_rcs[i] = RecordingChannel(index = i, coordinate = rc0.coordinate,
                                        name = rc0.name, description = rc0.description)
        
    new_rcgs = { }
    for k in old_rcgs:
        rcg0 = old_rcgs[k][0]
        new_rcgs[k] = RecordingChannelGroup(channel_indexes = rcg0.channel_indexes,
                                                                        channel_names = rcg0.channel_names,
                                                                        name = rcg0.name, description = rcg0.description)
        new_bl.recordingchannelgroups.append(new_rcgs[k])
        for i in old_indexes[k]:
            new_rcgs[k].recordingchannels.append(new_rcs[i])
    
    for bl in block_list:
        for seg in bl.segments:
            for anasig in seg.analogsignals:
                i = anasig.recordingchannel.index
                #~ anasig.recordinchannel = new_rcs[i]
                new_rcs[i].analogsignals.append(anasig)
    
    
    
    # merge units
    #TODO
    
    # merge segment
    for bl in block_list:
        for seg in bl.segments:
            #~ seg.block.id = new_bl.id
            new_bl.segments.append(seg)
        
    
    session.add(new_bl)
    session.commit()
    return new_bl


